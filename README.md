**Description**

This project performs automated checks for new posts on wg-gesucht.de. It sends a sound
notification if there are new posts matching predefined  user criteria.
You have to define your criteria from inside your profile in the website.
*Important*: If you don't have a profile and a predefined search filter, the program will not work. 

**Requirements**

1. Python 3.*
2. git
3. Download the most current selenium chrome driver from here:
https://googlechromelabs.github.io/chrome-for-testing/ \
and put 
the location of the exe file in the PATH.
4. Install the requirements.txt file with the following command:
``` bash
pip install -r requirements.txt
```

**Using this project**

1. Clone the project:
``` bash
git clone https://github.com/NIkolaStaykov/wg_gesucht_crawler.git
```
2. Create a config.json file following the template_config.json
3. Run the project with the following command:
``` bash
python crawler.py
```
