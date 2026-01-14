import React from "react";
import "./LandingPage.css";
import { useState,useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../../Assets/Reminder_Logo1_Notext.png";



function LandingPage () {
   

     const facts = [
        "Most vivid dreams happen during REM sleep, which repeats every 90–120 minutes.",
  "Your longest dreams occur in the early morning.",
  "You remember dreams better when you sleep in on weekends.",
  "Your muscles are paralyzed during REM to stop you from acting out dreams.",
  "Most dreams are visual with little sound or movement.",
  "Recurring dreams in children often involve monsters, falling, or being chased.",
  "Around 12% of people dream in black and white.",
  "Dreams often feel strange because the logic part of the brain shuts off.",
  "Most dreams reflect thoughts or events from the last 48 hours.",
  "You only dream of faces you’ve seen before — even briefly.",
  "Lower stress levels are linked to more positive dreams.",
  "Dreams last between 5 and 20 minutes each.",
  "Sex dreams make up only about 4% of all dreams.",
  "Men dream of multiple partners more than women.",
  "Women are twice as likely to dream about celebrities.",
  "Sleeping facedown increases the chance of vivid or sexual dreams.",
  "Sleep sex (sexsomnia) is a real sleep disorder, similar to sleepwalking.",
  "Nightmares are most common between ages 3 and 6.",
  "Women experience more nightmares during teen and adult years.",
  "Nightmares happen most often in the last third of the night.",
  "Recurring nightmares may indicate nightmare disorder.",
  "8% of people experience sleep paralysis.",
  "Grief dreams become more common during the holidays.",
  "Night terrors affect 40% of children but usually fade with age.",
  "Around 3% of adults still have night terrors.",
  "Eating before bed increases the chance of nightmares.",
  "Some medications (like antidepressants) cause more nightmares.",
  "Negative emotions (sadness, guilt, confusion) cause more nightmares than fear.",
  "Blind people dream with images.",
  "Pets experience REM sleep and dream as well.",
  "People forget 95–99% of their dreams.",
  "Most adults dream 4–6 times per night.",
  "Some people believe dreams can predict the future — but science disagrees.",
  "Negative dreams are more common than positive ones.",
  "Lucid dreaming techniques can teach you to control dreams.",
  "Sleep talking often includes swearing.",
  "Hypnic jerks cause the sensation of falling as you fall asleep.",
  "Teeth-falling dreams may be linked to jaw tension or grinding, not bad omens.",
  "Researchers still don’t fully understand why humans dream.",
  "Morning dreams are more emotional and detailed.",
  "Your brain is more active while dreaming than when awake.",
  "Dreaming helps process emotions and memories.",
  "Stress often increases dream intensity.",
  "Dream images can be metaphors for real-life struggles.",
  "Dreams can combine memories from years apart into one scene.",
  "People dream more when they’re sleep-deprived.",
  "Nightmares are more common during illness or fever.",
  "You can train yourself to remember dreams better by journaling."

     ];

     const [index, setIndex] = useState(0);
     const [fade, setFade] = useState(true);
    const [fadeOut, setFadeOut] = useState(false);
      const navigate = useNavigate();

     const handleContinue = () => {
  setFadeOut(true);

  // Wait one frame so the fade-out class is actually applied
  requestAnimationFrame(() => {
    setTimeout(() => {
      navigate("/login");
    }, 800); // match your CSS fade time
  });
};


     useEffect(()=> {
        const interval = setInterval(()=>{
            setFade(false);
            setTimeout(()=>{
                  setIndex(Math.floor(Math.random()*facts.length));
                  setFade(true);
            },500);
        },5000);

            
          
        return ()=> clearInterval(interval);
    },[]);

     return(
<div className={`LandingPage-Container page-fade-in ${fadeOut ? "fade-out" : ""}`}>


  <div className="stars"></div>
  <div className="stars2"></div>

  <div className="header-section">
    <img src={Logo} alt="Logo" className="landing-logo" />
    <h1>REMinder</h1>
    <p className="subtitle">Dream analysis</p>
  </div>

  <div className="quote-box">
    <p className={fade ? "fade-in" : "fade-out"}>{facts[index]}</p>
  </div>

  <button className="continue-button" onClick={handleContinue}>Continue</button>

</div>


);

}



export default LandingPage;



