<div align="center" markdown>


<img src="https://user-images.githubusercontent.com/106374579/183634421-0cb94591-5ea6-4de2-9fd2-fccb72b241d5.png"/>

# Resize-images

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/resize-images)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/resize-images)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/resize-images.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/resize-images.png)](https://supervisely.com)

</div>

# Overview

This application allows you to resize both images and their annotations. The result will be saved in a new project.

# How To Use

**Step 1.** Add an app to your team from Ecosystem

   Select `Ecosystem` in Main Menu -> `Transform` in Content -> `Resize images`
<img src="https://i.imgur.com/O0uy6v1.png"/>

**Step 2**: Open context menu of the project -> `Run` App` -> `Transform` -> `Resize images` 
<img src="https://i.imgur.com/w5pztbj.png" height="400px"/>

**Step 3.** Set target width and height
   
   The app contains three sections: a table displaying the top 10 most frequent image sizes, a field for custom target values (width and height) with checkboxes that enable equalising sides by automatically adjusting the selected one, and an input field with the resized project name.
   
![image](https://github.com/supervisely-ecosystem/resize-images/assets/61844772/8d86b7eb-9ba7-4529-b542-1f0492cb443a)

**Step 4.** Press the `Run` button. The progress bar will appear. Also, you can monitor progress from the tasks list of the current workspace.
   The app creates a new project and will appear as a thumbnail under the `Run` button.
