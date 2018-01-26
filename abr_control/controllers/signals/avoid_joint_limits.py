import numpy as np

from .signal import Signal


class AvoidJointLimits(Signal):
    """ Pushes  joints away from set limits

    Pass in a set of maximum and minimum joint angles, along with a maximum
    force to push away with. As the joints near their limit the opposing force
    gets larger until it reaches max_torque

    Parameters
    ----------
    min_joint_angles : np.array
        the lower bound on joint angles [radians]
    max_joint_angles : np.array
        the upper bound on joint angles [radians]
    max_torque : np.array, optional (Default: 1)
        the maximum force to push away with [Nm]
    cross_zero: List of Boolean, Optional
        (Default:[False, False, False, False, False, False])
        select whether the section of 2pi you want to work in crosses
        the zero-2pi boundary. Set to true if it does to account for odd
        behaviour when we jump from 0 to 2pi and vice versa
    gradient: List of Boolean, Optional
        (Default:[False, False, False, False, False, False])
        set if you want a gradual push from the limit, or a wall once reached
        True for gradient of force, False for a sudden opposing force (Wall)

    NOTE: use None as a placeholder for joints that have no limits
    """

    def __init__(self, robot_config,
                 min_joint_angles, max_joint_angles,
                 max_torque=None,
                 cross_zero=[False, False, False, False, False, False],
                 gradient=[False, False, False, False, False, False]):
        # shift limits to -pi to pi range
        for ii in range(0,len(min_joint_angles)):
            if min_joint_angles[ii] is not None:
                min_joint_angles[ii] = min_joint_angles[ii] - np.pi
            if max_joint_angles[ii] is not None:
                max_joint_angles[ii] = max_joint_angles[ii] - np.pi

        self.cross_zero = np.array(cross_zero)
        self.gradient = np.array(gradient)

        self.min_joint_angles = np.asarray(min_joint_angles, dtype='float32')
        self.max_joint_angles = np.asarray(max_joint_angles, dtype='float32')

        # flip in this case so math matches normal case
        temp_min = np.copy(self.min_joint_angles)
        temp_max = np.copy(self.max_joint_angles)
        self.max_joint_angles[cross_zero] = temp_min[cross_zero]
        self.min_joint_angles[cross_zero] = temp_max[cross_zero]

        print('===MIN LIMITS===: ', min_joint_angles)
        print('===MAX LIMITS===: ', max_joint_angles)

        if (self.max_joint_angles.shape[0] != robot_config.N_JOINTS or
                self.min_joint_angles.shape[0] != robot_config.N_JOINTS):
            raise Exception('joint angles vector incorrect size')
        # find where there aren't limits
        self.no_limits_min = np.isnan(self.min_joint_angles)
        self.no_limits_max = np.isnan(self.max_joint_angles)

        self.robot_config = robot_config
        self.max_torque = (np.ones(robot_config.N_JOINTS)
                           if max_torque is None else np.asarray(max_torque))


    def generate(self, q):
        """ Generates the control signal

        q : np.array
          the current joint angles [radians]
        """
        q = q - (np.ones(len(q)) * np.pi)  # shift to -pi to pi range

        # determines which direction to push based on what limit is closer
        closer_to_min_index = abs(q - self.min_joint_angles) >= abs(q - self.max_joint_angles)
        closer_to_max_index = abs(q - self.min_joint_angles) <= abs(q - self.max_joint_angles)

        # initialize arrays
        avoid_min = np.zeros(self.robot_config.N_JOINTS)
        avoid_max = np.zeros(self.robot_config.N_JOINTS)

        # get the minimum force between the exponential curve as q
        # approaches limit and max force if user wants a gradient
        # force field instead of hard stop
        avoid_min[self.gradient] = np.minimum(np.exp(1.0/(q[self.gradient]
                                                     - self.min_joint_angles[self.gradient])),
                                              self.max_torque[self.gradient])
        avoid_max[self.gradient] = -np.minimum(np.exp(-1.0/(q[self.gradient]
                                                      - self.max_joint_angles[self.gradient])),
                                              self.max_torque[self.gradient])

        # if passed limit set max torque
        min_index = (q - self.min_joint_angles) < 0
        max_index = (q - self.max_joint_angles) > 0

        # Check which limit is closer
        # Only affects joints who's working area crosses the 0-2pi threshold
        # check if in negative half of working area
        min_index[self.cross_zero] = (min_index[self.cross_zero]
                                      * ((q[self.cross_zero]
                                          - self.max_joint_angles[self.cross_zero]) > 0)
                                      * closer_to_max_index[self.cross_zero])
        # check if in positive half of working area
        max_index[self.cross_zero] = (max_index[self.cross_zero]
                                      * ((q[self.cross_zero]
                                          -self.min_joint_angles[self.cross_zero]) < 0)
                                      * closer_to_min_index[self.cross_zero])

        avoid_min[min_index] = self.max_torque[min_index]
        avoid_min[self.no_limits_min] = 0.0

        avoid_max[max_index] = -self.max_torque[max_index]
        avoid_max[self.no_limits_max] = 0.0

        self.u_avoid = avoid_min + avoid_max

        return self.u_avoid
