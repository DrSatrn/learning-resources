# learning-resources
A collection of hand-curated IT/CS tools, guides and blogs with automatic link validation and an HTML bookmark exporter so you can import them into your browser of choice.
## Disclaimer
I am not claiming ownership of any of the links contained within `resources.md`. Full credit to the authors and owners of these sites - I merely wanted to make them easier to find.
## Why did I start this project?
I'm 100% self-taught in IT and computer science.
Like many others, I ran into the same problem: there is a massive amount of content out there, but it's scattered everywhere - Reddit posts, GitHub repos, random blog posts, even mailing lists of all things.

I wanted to collate the best resources I found and centralise them into a single, easily accessible place.

Furthermore, I wanted a simple way to actually *use* the list.
That’s where the bookmark exporter comes in — once you’ve trimmed the list down, you can import it into your browser and forget about it. Easy ;P
## How it works
`resources.md` is the master file, this is what I update with new links.

- On merge and push we validate the links are healthy (no 404 'not found' etc)
- `links.txt` is cross-referenced against `resources.md` and updated if any links are missing
- links.txt is used to create a browser import file if one of the generate booksmarks scripts are run

I setup some simple CI to ensure;
- Markdown format is validated
- Included links work (we have a manual ignore list as well to account for some checks failing on known good sites)
- `links.txt` stays in sync with `resources.md`
## How to generate your own custom bookmarks
Now for the fun bit. Don't worry, I kept it as simple as possible.

Step 1. Clone the repo
```bash
git clone https://github.com/DrSatrn/learning-resources.git
```
Step 2. Trim links<br>
Edit `links.txt` and remove any you don't want to keep.
**Note**<br>
The list isn't in alphabetical order - it follows the same order as `resources.md` so cross referencing is easier.

Step 3. Generate the bookmarks file
```bash
generate-bookmarks.sh # or generate-bookmarks.ps1 if you are on a windows machine
```
Step 4. Import into your browser.<br>
The script would have created a new file in root of the repository (learning-resources-bookmark.html)
Import into your browser of choice.

Everything will be placed into a single folder (drsatrns-learning-resources).
You can organise it further if you want.

## Future Ideas
I have a number of goals and aspirations for this project. I'll list out a few high level ones;

- Serve as a static learning resource website along with images, a more detailed write-up and perhaos a review and a link out to a project if the resource is actually something that I spend time with.

- Better organisation of topics. It's mostly a flat resource dump at this point in time, I'd like to make it more intutive to navigate (this will be essential as the list grows).

- Perhaps most important of all; I'd like to create my own guiedes and resources from scratch! Using the list as an insipiration of course. Perhaps have my own `drsaturn-guides.md` where I teach you how to set infrastructure up from scratch on a home lab. I have some ideas but nothing concrete at this stage
