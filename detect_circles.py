# import the necessary packages
import numpy as np
import argparse
import cv2
import scipy.stats

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

# function for sending an sms when a relevant open parking spot is detected
def sms_send(i1, j1):
    # Your Account Sid and Auth Token from twilio.com/console
    # See http://twil.io/secure
    account_sid = 'AC53db240a4b8176618eedfd3877fb3943'
    auth_token = '78b4e1d0242e870e2de2d29d556c63e9'
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body="***A parking spot has been detected at http://goo.gl/maps/Nwquqa5E9NWarSBAA"+". The confidence level is "+str(j1)[:4]+"%.***",
                         from_='+18509903876',
                         to='+18566762891'
                     )

    print(message.sid)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
args = vars(ap.parse_args())

# load the image, clone it for output, and then convert it to grayscale
image = cv2.imread(args["image"])
image = cv2.resize(image, (0, 0), fx =1, fy=1)
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# detect circles in the image
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 2, 35, minRadius=6, maxRadius=10, param1=40, param2=36)

# This numpy function removes superfluous leading "1" dimension from circles
cir_squeeze = np.squeeze(circles)

# ensure at least some circles were found
if circles is not None:
    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")

    # loop over the (x, y) coordinates and radius of the circles
    for (x, y, r) in circles:
        # draw the circle in the output image, then draw a rectangle corresponding to the center of the circle
        cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

# calculate probabilities of potential parking spaces in the current image
# the probabilities are calculated between each wheel in the image
cir_squeeze = np.array([cir_squeeze[i] for i in np.argsort(cir_squeeze[:,0])])
x_distances = np.array([cir_squeeze[i+1,0]-cir_squeeze[i,0] for i,j in enumerate(cir_squeeze) if i < len(cir_squeeze)-1])
x_mean = [np.mean(np.delete(x_distances,i)) for i,j in enumerate(x_distances)]
x_std = x_distances.std(ddof=1)
x_score = np.array([abs(j-x_mean[i])/x_std for i,j in enumerate(x_distances)])
x_prob = [((scipy.stats.norm.cdf(i))) for i in x_score]

# if we detect a probability of a parking space with greater than 95 percent
# confidence, we send the user a text message notifying them
for i,j in enumerate(x_prob):
    if j > 0.95:
        sms_send(i,j)

# show the output image
cv2.namedWindow("Tires Dectected", cv2.WINDOW_NORMAL)
cv2.imshow("Tires Dectected", np.hstack([image, output]))

cv2.waitKey(0)
cv2.imwrite('images/tires_detected.jpg',output)
