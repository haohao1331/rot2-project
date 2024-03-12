import numpy as np

class KalmanFilter:
    def __init__(self, x0, P, A, B, H, Q, R):
        self.x = x0 # state
        self.P = P  # uncertainty covariance
        self.A = A  # state transition matrix
        self.B = B  # control input matrix
        self.H = H  # Measurement matrix
        self.Q = Q  # process noise covariance
        self.R = R  # measurement noise covariance

    def predict(self, u=0):
        # print(self.x.shape)
        self.x = self.A @ self.x + self.B @ u  # a priori state estimate
        # print(self.x.shape)
        self.P = self.A @ self.P @ self.A.T + self.Q    # a priori estimate covariance

    def update(self, z):
        assert z.shape == self.x.shape
        y = z - self.H @ self.x   # residual
        S = self.H @ self.P @ self.H.T + self.R  # residual covariance
        K = self.P @ self.H.T @ np.linalg.inv(S)    # Kalman gain

        self.x = self.x + np.dot(K, y)  # a posteriori state estimate
        self.P = (np.eye(len(self.x)) - K @ self.H) @ self.P    # a posteriori estimate covariance

if __name__ == '__main__':
    import pickle as pk
    import pandas as pd
    # Example
    x0 = np.array([[0], 
                   [0]])  # initial state
    P = np.eye(2) * 1000    # initial uncertainty
    A = np.array([[1.,1.],
                  [0.,1.]])   # state transition matrix
    H = np.array([[1., 0.]])   # Measurement matrix
    Q = np.eye(2) * 0.01    # process noise covariance
    R = np.array([[5.]])  # measurement noise covariance

    kf = KalmanFilter(x0, P, A, H, Q, R)

    # Measurements
    df = pk.load(open('/Users/yefan/Desktop/rot2/rot2-project/data/2024-02-13_first_mouse_test_SC23_analysis/trial2.pkl', 'rb'))
    zs = df['mouse_pos_x'].values
    print(zs)
    exit()
    zs = [np.array([1, 0]), np.array([0, 1]), np.array([1, 1]), np.array([0, 0])]

    for z in zs:
        kf.predict()
        kf.update(z)
        print(f'x: {kf.x}, P: {kf.P}')