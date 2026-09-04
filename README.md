# Transfer shape keys in a couple clicks
Blender addon for transfering shapekeys from on mesh to another one and binding thier values. There is another free addon that do almost the same with another algorythm (you may check it [here](https://github.com/fblah/ShapeKeyTransferBlender)), but sometimes it does not work properly. So have writen my own addon. It is very fast and simple (around a hundred lines of code).

# Support the Development
The addon is distributed for free, but you can support the dev via [Patreon](https://patreon.com/SqueezyPixels)

# How to transfer Shape Keys
1. Switch to object mode
2. Select a target mesh or multiple meshes
3. Select source mesh (it should be active, don't click at another object after that)
4. Specify which shape key you want to transfer (N-panel > Tools > Shape Key Wrap).
4.1. By default "Transfer By The List" option is disabled (toggle button is released) and all the shape keys of the source object to be transferred.
4.2. If "Transfer By The List" option is activeted (toggle button is pressed) only checked shape keys from the list will be transferred. "Refresh" button refreshes the list of the shape keys in accordance to all the shape keys of the source object. "Check All" refreshes the list and checks all the shape keys. "Uncheck All" refreshes the list and uncheckes all the shapekeys. 
5. N-panel > Tools > Shape Key Wrap > Click "Transfer Shape Keys".
6. Adjust parameters if something goes wrong (most of the parameters are the parameters of surface deform modifier, the addon is based on it). If "Replace Shapekeys" is on, and target mesh have shape key with the same names as source mesh they will be replaced. Be carefull with the checkbox because the key shape data may be lost irrecoverably. "Bind Values" binds the values of target shape keys ot the values of the source shape keys via drivers.
7. Optionally enable "Delete Empty". During a transfer, this scans only the shape keys created or replaced by that transfer. It removes a transferred key only when it has no displacement from the target mesh's Basis shape key. Existing target shape keys are not scanned or removed by this option.

# Remove Empty Shape Keys
The "Delete Empty Shape Keys" action in the Utils panel is separate from transfer and works on the active object only. With "Use List" disabled, it scans every non-Basis shape key on that object. With "Use List" enabled, it scans only the checked shape keys. This action is not limited to keys created by a transfer, so use it when you intentionally want to clean up existing shape keys.

# How to bind Shape Key values by names
By default the add-on will bind shape key values with the shape keys. But you can easily do it separately. 
1. Do steps 1-4 from the preceding paragraph (see above "How to transfer Shape Keys").
2. Click "Bind Values" button. The shape key values of the target object will be bound do shape keys of the values of the source shape keys with matching names. 

# Known issues
## Unable to bind surface deform modifier error
The problem is related to the inability to bind the surface deform modifier to the source mesh
- Check out the blender [Surface Deform Modifier documentation](https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/surface_deform.html) on target mesh validity and check your mesh. ShapeKeyWrap source is SurfaceDeform target so you need to check the mesh from which you transfer shape keys first of all. The most frequent problem is **"edges with more than two faces"**. **"concave faces"** is less frequent but also occurs. 
- When there no other problems but you still getting the error. Experimentally I got this behavior when a lot of vertices of target and source mesh have the same coordinates. I have found a few solutions:
   - Disabling modifiers can sometimes resolve this issue.
   - Shifting vertices of one mesh very slightly. You can add such noise enabling "Bind Noise" feature. Very slight noise value sometimes helps.
   - Let me know if you know other solutions

# Feedback and Support
Join our [Discord Server to](https://discord.gg/zGDqh2CsbJ) share your feedback and ask for help. **Please use right channel for feedback and suppor as I have a few add-ons.**

Also visit my [youtube channel](https://www.youtube.com/@squeezypixels) and [gumroad page](https://squeezypixels.gumroad.com/l/shapekeywrap) If you liked the addon

# Another Add-ons
- **[OmniMirror](https://www.artstation.com/a/55005989)** - Powerful symmetry workflow tools for Blender (paid).
- **[JoinAsPose](https://github.com/MykytaPetrenko/JoinAsPose)** - Free add-on for attaching the rest pose from one/multiple source armatures to a single target armature.
