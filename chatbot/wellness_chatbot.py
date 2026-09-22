def generate_response(message, emotion=None):

    message = message.lower()

    # -------------------------------------------------
    # Emotion-aware greeting
    # -------------------------------------------------

    if emotion == "Sad":
        emotion_message = """
💙 I noticed that your detected facial expression was **Sad**.

Remember that an emotion prediction from a photo is only an AI estimate and does not diagnose your mental health.

If you'd like, you can tell me what's bothering you.
"""
    
    elif emotion == "Angry":
        emotion_message = """
🌿 Your detected facial expression appears **Angry**.

You could try taking a few slow breaths, stepping away from a stressful situation, or taking a short break.

Would you like some stress-relief techniques?
"""

    elif emotion == "Fear":
        emotion_message = """
💙 Your detected facial expression appears **Fearful**.

Try taking slow, steady breaths and focusing on your surroundings.

If you'd like, I can guide you through a simple relaxation exercise.
"""

    elif emotion == "Happy":
        emotion_message = """
😊 Your detected facial expression appears **Happy**!

That's great. Keep doing activities that make you feel positive and connected.

Would you like some ideas for maintaining good wellbeing?
"""

    elif emotion == "Neutral":
        emotion_message = """
😌 Your detected facial expression appears **Neutral**.

Everyone has different expressions, so this result doesn't necessarily indicate how you're feeling internally.

You can still ask me anything about your wellbeing.
"""

    else:
        emotion_message = ""

    # -------------------------------------------------
    # User questions
    # -------------------------------------------------

    if "stress" in message:
        return emotion_message + """

🌿 **Stress Relief Tips**

• Take slow, deep breaths.
• Take a short break.
• Try meditation or light exercise.
• Talk to someone you trust.
"""

    elif "sleep" in message:
        return emotion_message + """

😴 **Better Sleep Tips**

• Aim for 7–9 hours of sleep.
• Avoid screens before bedtime.
• Keep a regular sleep schedule.
• Try relaxing before bedtime.
"""

    elif "anxiety" in message:
        return emotion_message + """

💙 **Anxiety Support**

• Take slow, controlled breaths.
• Focus on the present moment.
• Try a short walk.
• Talk to someone you trust.

If anxiety continues or seriously affects your daily life, consider speaking with a qualified professional.
"""

    elif "sad" in message or "sadness" in message:
        return emotion_message + """

💙 **When You're Feeling Sad**

• Talk to someone you trust.
• Do something you enjoy.
• Take a walk or get some fresh air.
• Give yourself time to rest.

You don't have to handle everything alone.
"""

    elif "happy" in message or "mood" in message:
        return emotion_message + """

😊 **Positive Mood Tips**

• Spend time with people you care about.
• Do activities you enjoy.
• Stay physically active.
• Get enough sleep.
• Celebrate small achievements.
"""

    elif "hello" in message or "hi" in message:
        return emotion_message + """

👋 **Hello! I'm your Wellness Assistant.**

You can ask me about:

🌿 Stress  
😴 Sleep  
💙 Anxiety  
😊 Mood  
🧘 Relaxation
"""

    else:
        return emotion_message + """

🤖 **Wellness Assistant**

I can help with general wellness information.

Try asking:

• How can I reduce stress?
• How can I sleep better?
• What can I do for anxiety?
• How can I improve my mood?
"""