# learning-resources
A collection of hand-curated IT/CS tools, guides and blogs with automatic link validation and an HTML bookmark generator so you can import them into your browser of choice.
## Disclaimer
I am not claiming any of the links contained within `resources.md` - full credit to the authors and owners of these sites. I merely wanted to make it that little bit easier to find them.
## Why did I start this project?
I'm 100% self-taught within the world of information technology and computer science.
Many people are; there is a massive amount of resources available online. The issue I and many other people have is knowing *where* to look for said resources. Everything is scattered around the interwebs; reddit posts, Github repos, random blog posts and mailing lists of all things. I wanted to collate the best ones I found and centralise them to a single easily accessible location.

What is more, I wanted an easy way to grab the resouces out and refer to them at a later date. That is why I added a small browser import file generator. Once you have found this list you can upload it to your browser and never have to worry about it again. Easy!
## How it works

## How to generate your own custom bookmarks
Now for the fun bit. Don't worry, I made it as simple as possible :)

Step 1. Clone the repo
```
git clone https://github.com/DrSatrn/learning-resources.git
```
Step 2. Modify links to be imported <br>
Trim any links you don't want to import from links.txt as this is consumed by the generate-bookmarks script. <br>**Please Note** &nbsp;&nbsp; ---> this list is not in alphabetical order, it follows the same order as `resources.md` which hopefully makes it easy to find links you want to keep/omit.

Step 3. Execute the relevant import script
```
generate-bookmarks.sh/ps1
```
Step 4. Import file into your browser
The above script will have generated an HTML file called `learning-resources-bookmark` in the root of the directory. 
Simply follow the steps to import this file into your browser of choice. 
They won't be organised by category, you will simply get a bookmark folder called drsatrns-learning-resources. It is up to you to further organise if you wish.

## Future Ideas
I have a number of goals and aspirations for this project. I'll list out a few high level ones;

- Serve as a static learning resource website along with images, a more detailed write-up and perhaos a review and a link out to a project if the resource is actually something that I spend time with.

- Better organisation of topics. It's mostly a flat resource dump at this point in time, I'd like to make it more intutive to navigate (this will be essential as the list grows).

- Perhaps most important of all; I'd like to create my own guiedes and resources from scratch! Using the list as an insipiration of course. Perhaps have my own `drsaturn-guides.md` where I teach you how to set infrastructure up from scratch on a home lab. I have some ideas but nothing concrete at this stage
