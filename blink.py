import hassapi as hass
import asyncio

# App to blink a light entity, either if it is a single entity
# or a light group, and restore the previous state for each entity.
# Call the blink app from HA by firing an event with 
#   event_type: blink_light
#   additional event data that can can be ommited or inlcuded:
#   entity_id: a light entity_id
#   max_brightness: 0 - 255
#   min_brightness: 0 - 255. Its easier on the eyes not to use 0 here.
#   on_duration: time in second the light is on.
#   off_duration: time in seconds the light is off.
#   rgb_color: a list, i.e [255, 200,0]
#   count: Number of times the light blinks.
#   transition: Transition time in seconds.

# You can call the app from appdaemon with:
# event_data = {'entity_id': light.livingrrom, 'count': 3, 'rgb_color': [255,200,100],
#               'on_duration': 2, 'off_duration' :1, 'min_brightness': 150
#              }
# self.fire_event('blink_light', **event_data)


class Blink(hass.Hass):
    EVENT_TYPE          = 'blink_light'

    LIGHT_ON_SERVICE    = 'light/turn_on'
    LIGHT_OFF_SERVICE   = 'light/turn_off'
    STATE_ON            = 'on'
    STATE_OFF           = 'off'

    ATTR_STATE          = 'state' 
    ATTR_COUNT          = 'count'
    ATTR_ENTITY         = 'entity_id'
    ATTR_BRIGHTNESS     = 'brightness'
    ATTR_RGB_COLOR      = 'rgb_color'
    ATTR_ON_DURATION    = 'on_duration'
    ATTR_OFF_DURATION   = 'off_duration'
    ATTR_MAX_BRIGHTNESS = 'max_brightness'
    ATTR_MIN_BRIGHTNESS = 'min_brightness'
    ATTR_TRANSITION     = 'transition'

    async def initialize(self):
        # Make a copy of the app args.
        self.DEFAULT_SETTINGS = dict(self.args)
        # Remove the module and class keys.
        self.DEFAULT_SETTINGS.pop('module', None)
        self.DEFAULT_SETTINGS.pop('class', None)

        # Listen for the HA event "blink_light".
        await self.listen_event(self.blink_lights, self.EVENT_TYPE)

        # Uncomment the below two lines to fire a blink_light event on when the app start. 
        # This is useful for testing the default settings.

        # event_data = {'count': 3, 'rgb_color': [255,200,100], 'on_duration': 2, 'off_duration' :1, 'min_brightness': 150}
        # self.fire_event(self.EVENT_TYPE, **event_data)

    async def blink_lights(self, event_type, data, kwargs):
        # Create a copy of the defalt settings.
        def_data = dict(self.DEFAULT_SETTINGS)

        # Override any default settings with settings from the event data.
        def_data.update(data)

        count   = def_data[self.ATTR_COUNT]
        entity  = def_data[self.ATTR_ENTITY]
        state   = await self.get_state(entity)
        
        # Check if the light entity is a light group.
        members = await self.get_state(entity, attribute=self.ATTR_ENTITY)
        if isinstance(members, list):
           pass
        else:
            # If the light entity isn't a light group, add the light entity to the members list.
            members=[]
            members.append(entity)

        entities = []
        for n in range(len(members)):
            entity_id = members[n]
            key = {}

            # Save the entity_id, state, brightness and rgb_color for each light entity to a dict and 
            # add the dict to the entities list.
            key[self.ATTR_ENTITY] = entity_id
            key[self.ATTR_STATE] = await self.get_state(entity_id)

            if key[self.ATTR_STATE] == self.STATE_ON:
            # If the light is "on", we can get the brightness and rgb_color directly.
                key[self.ATTR_BRIGHTNESS] = await self.get_state(entity_id, attribute=self.ATTR_BRIGHTNESS)
                key[self.ATTR_RGB_COLOR]  = await self.get_state(entity_id, attribute=self.ATTR_RGB_COLOR)
            else:
                # If the light is "off", we turn it on for a short while to get the brightness
                # and rgb_color.
                await self.call_service(self.LIGHT_ON_SERVICE, entity_id= entity_id)

                # Wait until the light is turned on.
                while await self.get_state(entity_id) == self.STATE_OFF:
                    await asyncio.sleep(0)
                # Save the brightness and rgb_color.    
                key[self.ATTR_BRIGHTNESS] = await self.get_state(entity_id, attribute=self.ATTR_BRIGHTNESS)
                key[self.ATTR_RGB_COLOR]  = await self.get_state(entity_id, attribute=self.ATTR_RGB_COLOR)
            # Save the light state to the entities list.
            entities.append(key)
    
        for x in range(count):
            # Turn on the light with MAX__BRIGHTNESS.
            await self.call_service(self.LIGHT_ON_SERVICE,  
                entity_id= def_data[self.ATTR_ENTITY],
                brightness = def_data[self.ATTR_MAX_BRIGHTNESS],
                rgb_color=def_data[self.ATTR_RGB_COLOR],
                transition=def_data[self.ATTR_TRANSITION])
            
            # Wait for ON_DURATION seconds.
            await asyncio.sleep(def_data[self.ATTR_ON_DURATION])

            # Turn on the light with MIN_BRIGHTNESS.
            await self.call_service(self.LIGHT_ON_SERVICE,
                entity_id= def_data[self.ATTR_ENTITY],
                brightness = def_data[self.ATTR_MIN_BRIGHTNESS],
                rgb_color=def_data[self.ATTR_RGB_COLOR])

            # Wait for OFF_DURATION seconds.   
            await asyncio.sleep(def_data[self.ATTR_OFF_DURATION])   

        for n in range(len(entities)):
            # Get previous state.
            entity_id = entities[n][self.ATTR_ENTITY]
            brightness = entities[n][self.ATTR_BRIGHTNESS]
            rgb_color = entities[n][self.ATTR_RGB_COLOR]

            # Restore previous state.
            await self.call_service(self.LIGHT_ON_SERVICE,
                    entity_id=entity_id,
                    brightness=brightness,
                    rgb_color= rgb_color,
                    transition=0)

            # If previous state was "off", turn off the light again.
            if  entities[n][self.ATTR_STATE] == self.STATE_OFF:
                await self.call_service(self.LIGHT_OFF_SERVICE,
                       entity_id=entity_id)

            
 
  
            

                
