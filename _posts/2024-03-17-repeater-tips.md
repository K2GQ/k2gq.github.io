---
layout: post
title: Repeater Operational Tips
subtitle: 
cover-img: /assets/img/acc_rc850.jpg
thumbnail-img: /assets/img/acc-rc-850-cib.jpg
share-img: /assets/img/acc_rc850.jpg
tags: [repeater,PL,CTCSS,controller,NE2S]
---
The question of how a repeater controller works has come up several times in the past few months.  Below are some relevant facts about the operation of a familiar repeater controller.  The post that follows will focus on high impact items for repeater users, including specific PL and timing details about our local VHF FM repeater, NE2S, on 146.595 MHz.

### PL (Private Line) / CTCSS
Continuous sub-audible tone signaling, required to access the repeater.  Input PLs help keep unwanted noise and unexpected users from activating the repeater.  While an input PL may be passed through the repeater, there is no PL tone generated on the output of NE2S by the repeater, so please keep your receive squelch set to carrier (do not filter on PL/CTCSS) for this repeater system.   Setting your radio for carrier squelch will ensure you will be able to hear the Courtesy Tone and repeater ID.

### Courtesy Tone
Following each user’s transmission, the repeater transmitter remains on for a programmable period with a Courtesy Tone provided to indicate that the other use may transmit. On NE2S, the value of this timer is set to 1.5 seconds.  The delay to the tone allows other stations to break into the conversation.  The period of 1.5 seconds starts when the user unkeys their microphone, and ends once the repeater Courtesy Tone sounds.

### Hang Time
This is the period where the repeater transmitter remains on the air, after the user input signal goes away and the courtesy tone has sounded.  Sometimes Hang Time is referred to as a repeater's tail.  NE2S is configured for 3 seconds of Hang Time after the Courtesy Tone.

### Timeout Timer
The repeater’s timeout timer is set at 3 minutes on NE2S and its function is to limit transmission duration in case of a continuous carrier at the repeater’s receiver. The timer resets automatically when the input signal at the receiver has ceased for 1.5 seconds. Normally, a Courtesy Tone is generated at that time, however if pending repeater ID is waiting, the repeater ID message will be generated in place of the Courtesy Tone and will be followed by the tone. In either case, the Timeout Timer resets at the beginning of the courtesy tone or pending repeater ID.  You do not need to wait for the repeater tail (Hang Time) to drop (end).  In order to reset the Timeout Timer, simply wait to hear the Courtesy Tone and begin the next transmission.

If users do not wait for the Courtesy Tone and the total transmission time between timer resets exceeds the NE2S timeout timer value of 3 minutes, the controller will announce “Repeater Time Out”, and the transmitter will be shut off. When the signal at the input stops for at least 1.5 seconds, the transmitter will be re-enabled and will announce “Repeater Ready” and normal operation will resume.

| Function | Value |
| :------ |:--- |
| Input PL | 127.3 Hz |
| Output PL | None |
| Courtesy Tone | 1.5 seconds |
| Hang Time | 3 seconds |
| Timeout Timer | 3 minutes |

73 & hope to hear you on the repeater soon!

