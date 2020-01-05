# IDD Final Project: Parky - AI Parking Assistant

#### Eduardo Castillo (EC833), Bar Kadosh (BK497), Ben Kadosh (BK499), & Jeremy Walker (JDW342)

<p align="center">
  <img src="Parky_Intro.png" width="600" height="420">
</p>

### Ideation 

The purpose of Parky is to bring real time parking and city dynamics information to citizens and drivers across large cities. Parky uses GPS and computer vision feature detection algorithms to detect the position of parking spaces around a city. Parky is envisioned as a low-cost embedded computing platform amenable for installation in any vehicle, from Uber and Lyft vehicles to food delivery bicycles.

As we began forming ideas and plans around our product, we realized that a major challenge would be mounting it to a vehicle (car, bike, etc.). The following two images capture the outcomes of our earliest brainstorming session:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9735.JPEG" width="600" height="420">
</p>

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9736.JPEG" width="600" height="420">
</p>

As can be seen in the first image, we imagined that our device would be a clear box with a Raspberry Pi + compatible camera and a breadboard inside. As we will discuss later on, this was very close to what we ended up building, minus the breadboard. Additionally, we ended up creating an opaque box, so the Raspberry Pi camera had to slightly poke out of the box to capture photos. 

Regarding attaching the device, the second image shows that we aimed to place it on the bottom of a car. However, we soon realized that this would be a tricky attachment point, mainly because the field of vision might be obstructed by components and wheels on the bottom of the car. Instead, we shifted to trying to mount to the side view mirror.   

### Cardboard Prototype

We ended up pivoting to the driver sideview mirror because we believed it would allow for a wide field of vision, which is necessary for tracking cars and the distances between them. While this means that the camera might be obstructed by traffic on the opposite side of the street at times, we worried that placing it on the passenger side would severely limit the field of vision and make our product ineffective. The photos below show our cardboard prototype construction process and the prototype being mounted to a car with a C-clamp mechanism:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9738.JPEG" width="600" height="700">
</p>

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9741.JPEG" width="600" height="700">
</p>

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9743.JPEG" width="600" height="700">
</p>

Through our ideation and prototyping processes, we were also better able to identify the components that our final product would require. Since the product would be portable, we needed a portable battery to power it — we settled upon the Raspberry Pi 3 B+ Battery Pack 4000mAh with suction so that we could easily attach it or attach to it. When designing our prototype, we also realized that an easy replacement for the cardboard box would be a Kugi Raspberry Pi case with all holes already in place for easy access. Lastly, we realized that a small Raspberry Pi camera would be ideal, so we ordered the Raspberry Pi Mini Camera Video Module 5 Megapixels 1080p Sensor OV5647 Webcam. All of these components are shown below:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/components.jpg" width="600" height="700">
</p>

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/cam.jpg" width="600" height="700">
</p>

### Control Flow
The control flow for Parky is dictated by GPS location. The GPS will trigger when images should be taken by the camera, which in turn will be processed by our computer vision module to determine if we have encountered an open parking spot, which will then send an API call if we have in fact found an open parking spot. There are two major reasons for relying on GPS to determine when to take photos: 

1) Often, cars and bikes are idle in cities (red lights, people getting in and out, etc.) and we do not wish to take duplicate photos of the same location and store the resulting repetitive information. 

2) Relying on time alone to take photos (every .3 seconds for example) does not account for vehicle speed. A car driving 40 mph and a bike moving at 15mph will cover different amounts of distance in the same period of time, and thus, we could miss a lot of potential open spots if we do not account for speed. GPS allows us to do that. 

This process of triggering the camera to take a photo once a large enough change in longitude or latitude has occurred and then processing those photos for open parking spots will occur in a while loop until the program can no longer detect GPS coordinates, meaning until the GPS has been turned off. 

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG-20191214-WA0000.jpg" width="600" height="380">
</p>

### GPS

For the prototype version we built, we used an iPhone app called GPS2IP. The app allows us to access the phone’s IP address and from there, we could extract the GPS coordinates with a curl command. The app was great for this step in the development of the product, as we could use an off the shelf product to give us the necessary coordinates. The main pieces of information we could extract from the app were the time, longitude, and latitude (along with additional information that we did not need). From this information, we were able to parse the long string of data into the necessary fields we required, namely longitude and latitude. Our framework would then process the changes in both latitude and longitude to assess if a large enough change in either component occurred, in which case we would trigger the camera to take a new photo. 

Furthermore, given the magnitude of distance that could be captured by GPS coordinates, and given the small changes in location between parking spots, we had to spend some time fine-tuning how small of a threshold for change in distance we should set to trigger photos. We ultimately settled on a very small threshold of greater than 0.0001 to fit the small changes corresponding to parking spots. 

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9823.jpeg" width="600" height="750">
</p>

### Computer Vision

The parking spot detection algorithm can be broken down into three main steps: image processing, space pooling, and space notification. 

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/demo_picture_small.jpg" width="600" height="100">
</p>

The image processing step takes in raw images from the camera (like the one above) and scans for simple features with a circular shape, using an open source image processing library which implements the Hough Circle Transform. The transform is a lightweight algorithm that analyzes potential circles based on the shape of the normal gradient around a certain edge, without regard to the nature of the object (i.e.: a baseball versus a car tire). Following detection, each distance (i.e.: between pairs of circles) is compared to the average distance for all of the other consecutive circles (horizontally aligned) detected in the image. Using a normal distribution assumption, we “pool” the “Z” value for the width of the detected distance (based on the centers of the circles). If the Z value obtained is higher than 0.95 (this was an arbitrary threshold assigned for pilot testing), the “space pooling” function calls the "space notification" function. Our algorithm detecting the wheels of an image can be seen in the photo below:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9825.JPG" width="600" height="420">
</p>

Furthermore, additional feature detection would be run for those pictures that meet the detection threshold (much smaller population implies drastically lower computational expense) to enable detection of relevant objects such as a construction cone, a fire hydrant, etc. The algorithm could also extract the model of the surrounding vehicles – using existing algorithms – in order to provide a more detailed and accurate assessment of the potential space prior to user notification.

### Notification API

The "space notification" function makes an API call to notify the users of a possible parking space via text message. Future implementations would evaluate GPS locations of pictures against public parking regulation APIs prior to notifying users of the availability of a spot (i.e.: using  data from the NYC DOTMAP PORTAL at https://www.nycdot.info). The following is an example notification sent by the "space notification" function:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/api.jpg" width="600" height="700">
</p>

### Final Device

To design the hardware for our device, we first measured and modeled all of our components in Solidworks (battery, raspberry pi, and camera). We then designed a shelled box that fit the dimensions of stacking the raspberry pi on top of the battery. As can be seen in the model below, we added two blocks that would constrain the battery in the horizontal direction:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/box_cad.png" width="600" height="700">
</p>

Next, we modeled a hole that would allow the camera to poke out of the box with the flat base of the camera sitting right on the inner face of the box. This made it very easy to simply tape the camera to the box:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/cam_cad.png" width="600" height="700">
</p>

A model of the interior of our box (with all of the components) is below. We used a 3D printer with this model to create our device:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/assem_cad.png" width="600" height="700">
</p>

As can be seen, there is a slit on the top layer of the box. This was created so that once all of the componenets are placed inside of the box, a lid can easily slide through the slit to close the box. This mechanism also makes it very easy to access the components if anything breaks or needs to be changed. When placing the components inside of the box, we used glue dots to secure the battery-raspberry pi combination in the 3rd dimension. The other two dimensions were constrained by the design of the box. 

The final box and lid after being 3D printed are below. After printing, we used sand paper to fix any deformities and give the box a nice finish:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/IMG_9794.JPEG" width="600" height="700">
</p>

The last phase involved attaching the device to a bike. We ended up using a bike instead of a car because it was much easier to access. We then attached square zip tie mounts to the back of the box (the zip tie mounts were adhesive-backed, holding the box quite nicely). We then used zip ties to attach the box to the front of the bike. This process involved a few challenges and considerations: we wanted to ensure that the palcement of the box did not interfere with one's ability to ride the bike, that a biker's limbs did not obstruct the camera, and that the device moved properly when the biker turned the wheel. Placing the box on the front rod of the bike ensured that the first two goals were met, but we were intially having issues with the box hitting other cables when we tried to turn the wheel. To fix this, we moved the box higher up on the rod and zip tied the surrounding wires to the main rod so that they would not be in the way.  A photo of the device attached to the bike is below:

<p align="center">
  <img src="https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/device_bike.jpg" width="600" height="700">
</p>

### Integration and Demo 

Once we attached the finalized device to the bike, we rode it around Cornell Tech to verify that it was working properly. A video of our product working in action is below!

[Parky in Action!](https://www.youtube.com/watch?v=cwewLBq8r5M&feature=youtu.be)

___________________________________________________________________________________________________________________________________________

### Code and CAD Files

[GPS Code](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/parky_gps.py)

[Computer Vision Code](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/detect_circles.py)

[Pi Camera](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/raspi%20camera.SLDPRT)

[Raspberry Pi](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/raspi.SLDPRT)

[Battery](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/battery.SLDPRT)

[Box Lid](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/lid.SLDPRT)

[Main Box](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/case.SLDPRT)

[Parky Assembly](https://github.com/jwalker34/Interactive-Lab-Hub/blob/master/Parky/parky.SLDASM)
