# appdemon-blink-app
Appdaemon app to blink lights in Home Assistant

A simple app to blink a single light entity or a light group, and then restore the light to its previous state.
If a light group is used, each individual light is restored to its previous state, even if the light was off, ie. when
turned on again, the color and brightness is unchanged.

Save the blink.py file in the apps folder and put the following in apps.yaml
```yaml
blink:
  module: blink
  class: Blink
  type: blink
  entity_id: light.master_bedroom
  max_brightness: 255
  min_brightness: 180 # Avoid using zero here, it's easier on the eyes with 100-150.
  rgb_color: [255, 200, 100] # Natural light bulb color.
  on_duration: 2
  off_duration: 1
  count: 4
  transition: 0
  ````
  
  Blink a light from Home Assistant by firing an event with 
  ```yaml
  event_type: blink_light
  ````
  
  Additional data that can be passed: (all are optional)
  ````yaml
  type: defaults to blink. The only other option is color_loop.
  entity_id: light.master_bedroom # Single light entity or a light group.
  max_brightness: 0 - 255
  min_brightness: 0 - 255
  rgb_color: A list i.e. [255, 200, 100] # Natural light bulb color.
  on_duration: Decimal or integer. Seconds the light is on. 
  off_duration: Decimal or integer, Seconds the light is off.
  count: 4. Number of blinks.
  transition: Decimal or integer. Transition time from off to on in seconds.
  ````
  
  To make a color loop, add the following keys:
  ````yaml
  type: color_loop
  color_loop: [ [255,0,0], [0,255,0] ] # Loop from red to green. You can add any number of colors to the list.
  max_brightness: 0-255 # max _brightness is used for all colors in the color loop.
  count: integer. Number of times the color loop is looped through.
  on_duration: Time between color transitions in seconds.
  transition: An integer. Must be smaller than on_duration.
  
  To fire the event directly from Appdaemon, use these lines:
  ````python
event_data = {'type': 'blink', 'entity_id': 'light.livingroom', 'count': 3, 'rgb_color': [255,200,100],
                'on_duration': 2, 'off_duration' :1, 'min_brightness': 150
               }
self.fire_event('blink_light', **event_data)
````

  
