# Transfer shape keys in a couple clicks
Blender addon for transfering shapekeys from on mesh to another one. There is another free addon that do almost the same with another algorythm (you may check it here https://github.com/fblah/ShapeKeyTransferBlender), but sometimes it does not work properly. So have writen my own addon. It is very fast and simple (around a hundred lines of code).

# How to use
1) Switch to object mode
1) Select a target mesh or multiple meshes
2) Select source mesh (it should be active, dont click any other object after that)
3) N-panel > Tools > Shape Key Wrap > Click "Transfer from Active".
4) Adjust parameters if something goes wrong (most of the parameters are the parameters of surface deform modifier, the addon is based on it). If "Replace Shapekeys" is on, and target mesh have shape key with the same names as source mesh they will be replaced. Be carefull with the checkbox because the key shape data may be lost irrecoverably.


If you liked the addon, visit my [youtube channel](https://www.youtube.com/channel/UCK95ry5O6RvofrR6qs5aBZA) and  [gumroad page](https://squeezyweasel.gumroad.com/l/shapekeywrap)
