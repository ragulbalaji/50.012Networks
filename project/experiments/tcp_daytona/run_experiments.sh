sudo python3 mininetTopo.py --client="normal" --server="linux" --cong-control="cubic"
sudo python3 mininetTopo.py --client="splitACK" --server="linux" --cong-control="cubic"
sudo python3 mininetTopo.py --client="dupACK" --server="linux" --cong-control="cubic"
sudo python3 mininetTopo.py --client="opACK" --server="linux" --cong-control="cubic"

sudo python3 mininetTopo.py --client="normal" --server="linux" --cong-control="reno"
sudo python3 mininetTopo.py --client="splitACK" --server="linux" --cong-control="reno"
sudo python3 mininetTopo.py --client="dupACK" --server="linux" --cong-control="reno"
sudo python3 mininetTopo.py --client="opACK" --server="linux" --cong-control="reno"

# sudo python3 mininetTopo.py --client="normal" --server="linux" --cong-control="vegas"
# sudo python3 mininetTopo.py --client="splitACK" --server="linux" --cong-control="vegas"
# sudo python3 mininetTopo.py --client="dupACK" --server="linux" --cong-control="vegas"
# sudo python3 mininetTopo.py --client="opACK" --server="linux" --cong-control="vegas"

python3 plot.py
sudo python3 -m http.server 80
