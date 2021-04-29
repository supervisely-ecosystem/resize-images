<div align="center" markdown>
<img src="https://i.imgur.com/R0d7RSW.png"/>

# Resize-images

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/resize-images)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/resize-images)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/resize-images&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/resize-images&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/resize-images&counter=runs&label=runs)](https://supervise.ly)

</div>

# Overview

This application allows to resize both images and their annotations. The result  will be saved in a new project. 

# How To Use

**Step 1.** Add app to your team from Ecosystem

   Select `Ecosystem` in Main Menu -> `Transform` in Content -> `Resize images`
<img src="https://i.imgur.com/gqVIOzl.png" width="800px"/>

**Step 2.** Run from context menu of project

   Go to `Context Menu` (images project) -> `Run App` -> `Transform` -> `Resize images` 
<img src="https://i.imgur.com/w5pztbj.png" height="400px"/>

**Step 3.** Set target width and height
   
   App contains 2 sections: fields for custom target values(width and height) and information about output team, workplace, project name. 
<img src="https://i.imgur.com/yg48K7K.png" height="400px"/>

**Step 4.** Press `Run` button. The progress bar will appear in `Output` section. Also you can monitor progress from tasks list of the current workspace.
   App creates new project and it will appear in `Output` section. Once you are ready with the app, you should close app manually
