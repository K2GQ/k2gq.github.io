---
layout: post
title: Repeater Operational Tips
subtitle: 
cover-img: /assets/img/acc_rc850.jpg
thumbnail-img: /assets/img/acc-rc-850-cib.jpg
share-img: /assets/img/acc_rc850.jpg
tags: [repeater,PL,CTCSS,controller,NE2S]
---
The question of how a repeater controller functions has come up several times in the past few months.  Below are some general facts about the operation of a familiar repeater controller that focus on relevant, high impact items for repeater users, with specific details for our local repeater, NE2S, on 146.595 MHz.

### PL (Private Line) / CTCSS
Continuous sub-audible tone signaling.  While PLs may be passed through the repeater, there is no PL generated on the output of NE2S, so please keep your receive squelch set to carrier (do not filter on PL) for this repeater system.  Setting your radio for carrier squelch will ensure you will be able to hear the Courtesy Tone and repeater ID.

### Courtesy Tone
Following each user’s transmission, the repeater transmitter remains on for a programmable period with a courtesy tone provided to indicate that the other use may transmit. On NE2S, the value of this timer is set to 1.5 seconds.  The delay to the tone allows other stations to break into the conversation.  The period of 1.5 seconds starts when the user unkeys their microphone, and ends once the repeater Courtesy Tone sounds.

### Hang Time
This is the Period that repeater transmitter stays on after input signal goes away and the courtesy tone has sounded.  Sometimes referred to as a repeater's tail.  NE2S is configured for 3 seconds of Hang Time, this period starts once the Courtesy Tone has sounded, and ends once the repeater ceases transmission.

### Timeout Timer
The repeater’s timeout timer is set at 3 minutes on NE2S, and its function is to limit transmission duration in case of a continuous carrier at the repeater’s receiver. The timer resets automatically when the input signal at the receiver has ceased for 1.5 seconds. Normally, a Courtesy Tone is generated at that time, however if pending repeater ID is waiting, the repeater ID message will be generated in place of the Courtesy Tone and will be followed by the tone. In either case, the Timeout Timer resets at the beginning of the courtesy tone or pending repeater ID.  You do not need to wait for the repeater tail (Hang Time) to drop / cease in order to reset the Timeout Timer, simply wait for the Courtesy Tone and begin the next transmission.

If users do not wait for the Courtesy Tone and the total transmission time between timer resets exceeds the NE2S timeout timer value of 3 minutes, the controller will announce “Repeater Time Out”, and the transmitter will be shut off. When the signal at the input goes away for at least 1.5 seconds, the transmitter will be re-enabled and will announce “Repeater Time Out Cancel” and normal operation will resume.

73 & hope to hear you on the repeater soon!

