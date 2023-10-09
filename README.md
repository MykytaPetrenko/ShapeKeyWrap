# Transfer shape keys in a couple clicks
Blender addon for transfering shapekeys from on mesh to another one and binding thier values. There is another free addon that do almost the same with another algorythm (you may check it here https://github.com/fblah/ShapeKeyTransferBlender), but sometimes it does not work properly. So have writen my own addon. It is very fast and simple (around a hundred lines of code).

# How to transfer Shape Keys
1. Switch to object mode
2. Select a target mesh or multiple meshes
3. Select source mesh (it should be active, don't click at another object after that)
4. Specify which shape key you want to transfer (N-panel > Tools > Shape Key Wrap).
4.1. By default "Transfer By The List" option is disabled (toggle button is released) and all the shape keys of the source object to be transferred.
4.2. If "Transfer By The List" option is activeted (toggle button is pressed) only checked shape keys from the list will be transferred. "Refresh" button refreshes the list of the shape keys in accordance to all the shape keys of the source object. "Check All" refreshes the list and checks all the shape keys. "Uncheck All" refreshes the list and uncheckes all the shapekeys. 
5. N-panel > Tools > Shape Key Wrap > Click "Transfer Shape Keys".
6 Adjust parameters if something goes wrong (most of the parameters are the parameters of surface deform modifier, the addon is based on it). If "Replace Shapekeys" is on, and target mesh have shape key with the same names as source mesh they will be replaced. Be carefull with the checkbox because the key shape data may be lost irrecoverably. "Bind Values" binds the values of target shape keys ot the values of the source shape keys via drivers.

# How to bind Shape Key values by names
By default the add-on will bind shape key values with the shape keys. But you can easily do it separately. 
1. Do steps 1-4 from the preceding paragraph (see above "How to transfer Shape Keys").
2. Click "Bind Values" button. The shape key values of the target object will be bound do shape keys of the values of the source shape keys with matching names. 

# Known issues
Empty shape keys are created on the target meshes. The problem is related to the inability to bind the surface deform modifier to the source mesh, and disabling modifiers can sometimes resolve this issue. A "Disable Modifiers" checkbox has been added, which temporarily disables all modifiers of the source mesh to address this issue. However, the add-on will still create empty shape keys in cases when Blender's surface deform modifier binding operation ends with an error (for example, when the mesh contains edges adjacent to three or more faces).

# Feedback and Support
Join our [Discord Server to](https://discord.gg/zGDqh2CsbJ) share your feedback and ask for help
Also visit my [youtube channel](https://www.youtube.com/@squeezypixels) and [gumroad page](https://squeezypixels.gumroad.com/l/shapekeywrap) If you liked the addon
