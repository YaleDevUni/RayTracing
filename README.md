# RayTracing

Simple Ray Tracer implemented by Python from scratch. This program is using 
reverse tracking ray trace and Phong Illumination Model. 
Input file is formatted text file, and output file format is ppm(P3)

- Usage:
    ```
    Python3 RayTracer.py InputFileName
    ```
- Feature
    - Support non-uniform ellipsoid
    - Support multiple light source

- Input File Format
    - The near plane**, left**, right**, top**, and bottom**
    - The resolution of the image nColumns* X nRows*
    - The position** and scaling** (non-uniform), color***, Ka***, Kd***, Ks***, Kr*** and the specular exponent n* of a sphere
    - The position** and intensity*** of a point light source
    - The background colour ***
    - The scene’s ambient intensity***
    - The output file name

Note that: * int, ** float, *** float between 0 and 1

Sample Output:
![N|Solid](/images/SampleOutput.png)