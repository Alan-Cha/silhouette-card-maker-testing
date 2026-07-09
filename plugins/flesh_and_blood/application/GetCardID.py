from plugins.flesh_and_blood.domain.Pitch import Pitch

async def get_card_id(name: str, pitch: Pitch):
    pitch_string = None if pitch == Pitch.NONE else pitch.name
    
    return name if pitch_string == None else f'{name} {pitch_string}'