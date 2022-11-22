import speake3

engine = speake3.Speake() # Initialize the speake engine
engine = speake3.Speake() # Initialize the speake engine
engine.set('voice', 'en')
engine.set('speed', '107')
engine.set('pitch', '99')
engine.say("Hello world!") #String to be spoken
engine.talkback()
