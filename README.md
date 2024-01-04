# Background

I've made https://github.com/wschoot/gpx-to-fit public but mainly see this as inspiration as it may be a bit rough around the edges. The usecase for myself mainly is to have a GPX with some waypoints I want to visit in optimal order using Up Ahead on my Garmin watch. I then load the GPX with the waypoints into Garmin Basecamp which allows me to create a track (not a route) using "Optimize" to calculate the best route. the gpx-to-fit.py script combines this into something my Fenix 7 understands.

# Requirements

Install some required Python modules

```bash
pip install -r requirements.txt
```
The supplied `wijkrondje.gpx` consists of three (gpx) waypoints in a GPX track (not a route!) which this tool converts to (fit) course points. It keeps the (gpx) trackpoints and adds them to the (fit) courserecords. It also adds some turn by turn directions but they don't appear on my Garmin up ahead yet.

```xml
$ cat wijkrondje.gpx | grep -v '<ele>' | grep -v '</trkpt>' | egrep '(trk|w)pt '
<wpt lat="52.22942903637886" lon="6.909052999690175">
<wpt lat="52.228858983144164" lon="6.909189959987998">
<wpt lat="52.228820007294416" lon="6.908142976462841">
<trkpt lat="52.228820007294416" lon="6.908142976462841">
<trkpt lat="52.228775750845671" lon="6.90809553489089">
<trkpt lat="52.228832244873047" lon="6.907954216003418">
<trkpt lat="52.22900390625" lon="6.907997131347656">
<trkpt lat="52.229068279266357" lon="6.907975673675537">
<trkpt lat="52.229454517364502" lon="6.908833980560303">
<trkpt lat="52.229561805725098" lon="6.909070014953613">
<trkpt lat="52.229433646425605" lon="6.909102955833077">
<trkpt lat="52.22942903637886" lon="6.909052999690175">
<trkpt lat="52.229433646425605" lon="6.909102955833077">
<trkpt lat="52.228810787200928" lon="6.909263134002686">
<trkpt lat="52.228864682838321" lon="6.909249387681484">
<trkpt lat="52.228858983144164" lon="6.909189959987998">
<trkpt lat="52.228864682838321" lon="6.909249387681484">
<trkpt lat="52.228810787200928" lon="6.909263134002686">
<trkpt lat="52.228767871856689" lon="6.909263134002686">
<trkpt lat="52.228553295135498" lon="6.908855438232422">
<trkpt lat="52.228531837463379" lon="6.908769607543945">
<trkpt lat="52.228531837463379" lon="6.908705234527588">
<trkpt lat="52.228832244873047" lon="6.907954216003418">
<trkpt lat="52.228775750845671" lon="6.90809553489089">
<trkpt lat="52.228820007294416" lon="6.908142976462841">
```

# Running the script

Run the command
```bash
python3 gpx-to-fit.py wijkrondje.gpx
```

# GPX view in Garmin Basecamp
<img width="668" alt="image" src="https://github.com/wschoot/gpx-to-fit/assets/3919193/f87dc183-5d7a-43e6-bcfc-60ac0727bed2">

# FIT view in Fit File Viewer
![image](https://github.com/wschoot/gpx-to-fit/assets/3919193/d4bee579-1eb5-4f73-85cb-678f0f113e39)

# Usage
Place the resulting `wijkrondje.gpx.fit` on your Garmin device in the \NEWFILES folder.
