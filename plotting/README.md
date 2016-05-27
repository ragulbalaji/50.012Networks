Plotting graphs
===============

Bytes/s vs time, for different numbers of victims
-------------------------------------------------

1. Inside each numbered directory, run the included program to generate a
CSV with the total number of bytes sent by all the victims each second:

    ```
    python total-bytes-per-sec.py *.csv > ../N.csv
    ```

where _N_ is the number of victims (1, 2, 4, etc.).

2. Up one directory, you should now have 1.csv, 2.csv, 4.csv, etc. Run the
GNUPlot script to generate the plot:

    ```
    gnuplot total-bytes-per-sec.plt
    ```

3. The plot will be saved as output.png.

Animated scatter plot
---------------------

The animated scatter plot shows the cumulative number of bytes output by a single victim.

1. Run the animation generation script. You may need to adjust some constants
at the top of the file, such as the location of FFmpeg on your system or the
name of the CSV file.

    ```
    python animated-scatter-plot.py
    ```

2. The animation will be saved as basic_animation.mp4
