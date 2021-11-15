# cs244_TCPDaytona
Provision an n1-standard-2 (2 vCPUs, 7.5 GB memory) Google Cloud instance
running Ubuntu 16.04. Allow HTTP and HTTPS traffic.

![gcloudimage](https://github.com/pavmeh/cs244_TCPDaytona/blob/master/readme/gcloud.png)

SSH in and install git if needed:
```
sudo apt-get update
sudo apt-get install git
```

clone repo and cd into the directory:
```
git clone https://github.com/pavmeh/cs244_TCPDaytona/
cd cs244_TCPDaytona
```

Run ``` ./setup.sh ``` to install all the dependencies. Press Y if prompted
(Note: DO NOT run this with ```sudo```, since this will not install the
dependencies correctly). If this breaks, run the commands in the script
individually in the terminal. This needs to be run only once per VM
instance.

Run ```./run_experiments.sh``` to run the experiment. It will take
approximately 1 minute to run. An http server is automatically create that
can be used to view the data files created (.png) by using the external
IP shown on the Google Cloud Platform Manager for the VM instance. The URL
used in your local browser should be of the form:
```
http://<external IP>/<name of file>
```

The png files available should be named ```data.reno.png``` and ```data.cubic.png```.

From here, simply type in the name of the png file you wish to view after the
slash, as shown above. Kill the server with ```ctrl+C``` when done.

If you wish to run the experiment again, run ```./cleanup.sh``` first. This
deletes the previous data files.
