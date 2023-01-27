# MacOS Music Discord Wrapper

Bascially program flow goes something like this:

- Use AppleScript to expose data about the Music app to python
- Use this data to create the Discord RPC
- At the moment usese the iTunes API to get album art - this may change
    - Caching has been implemented here to reduce the amount of get requests to Apple as well as improving efficiency.

Das about it.  

&nbsp;
&nbsp;


# To-Do
- Write the program 
- Create my own rich presence wrapper cuz i dont need all the features
- Get Album Artwork for Song
- Add Last.Fm Integration
    - Scobbling?
    - Add button to users last.fm page.
- Refactor into Node.Js and use the Discord Game SDK
    - Learn how to use Node.JS
- 


&nbsp;
&nbsp;

# Libraries Used

- [![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

