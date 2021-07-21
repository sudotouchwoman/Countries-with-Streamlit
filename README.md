## **Dockerized streamlit+flask project about informational context within various countries**

## **To run this app:** make sure you have your dependencies installed via `pip install -r requirements.txt`. App is consisted of 2 main parts currently, so you are likely to just go `python server.py` and `streamlit run app-usage.py`

## _Tiny spoiler:_ i actually have not been working on the very **nlp** staff that _creates the data_ for my app, the goal was in the following:
+ **Python practice** in every way: from basic things like os and numpy to more complex and data-aimed modules like networkx, schema, pandas. i also used some basic visualisation with matplotlib & pyvis and web-related stuff like flask & requests.
+ **Docker practice** - the apps should be containerized to start CI/CD pipeline. i personally find it wonderful and especially the inner-network feature in compose which lets the services speak and listen to each other at ease.
+ **Git, actually**. i am really grateful to git and github environment to let lots of users create everywhere and get shit done, thorough i haven't yet felt the entire power of branches and merges.
+ **Overall awareness**. mostly working with front-side, i fell like it may be interesting, especially while using amazing streamlit framework. Python has great ecosystem and agility (`pip install whateveryouwant`), i adore the fact how you can just get focused on the business-process and get to know something new, actually, like HTTP protocol usage or neural network creation.
## **I decided to code app once again (almost) from scratch**
## The biggest flaw of project i have been working on for last month was the lack of expierence. i may still be unexpierenced, however i found some ways to improve the app architecture:
+ First app had _almost_ everything wrapped by `streamlitapp` class. later i extracted some parts into `DisplayGraph` and `DataStorage` classes. But it was still not enough, everything felt too straightforward and dull.
+ App could not **interact with back-end** properly. Even integration with self-written tiny testing flask server became pain in the ass. Now i **refactored all the JSON's** and changed data insertion so that UI additional components are loaded (either from server if available or from local file) at first: lists of options for selectboxes, for example (something we cannot pre-fill while desiring app to be able to be up-to-date). Then actual content is loaded, and **the request params** are what is great here: now everywhere requests are done with same interface. yep, it is imperfect, but i have done my current best. I have been coding for about 8 hours since last evening (i struggle to be punctual)
## **Current TODO** contains:
+ Finishing refactoring code, currently page 3 is not even started. Also add some links to download content.
+ Adding compose yaml for this project and testing app in container. Afterwards i will also
+ Adding some tests and documentation for docker
+ Adding data validation with Schema for loaded things. I have actually filled Postgre DB with some project datasets and can guess how input data would look like.