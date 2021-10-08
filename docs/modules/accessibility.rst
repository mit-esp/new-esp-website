#####################
Accessibility (a11y)
#####################

Accessibility, like nearly all engineering problems, has a wide range of being good enough versus not good enough. 
Determining what level you are aiming for, and figuring out what are the cost-effective wins are key to success. 
There is a wide spectrum of blindness and deafness, but at some point you will hit a trade-off where you would be hurting 
the user experience of your majority user base if you were to help make your website more usable for a small minority 
of users. So there is a difficult engineering challenge here of keeping things accessible, without interfering 
with the user experience of most users, without interfering with the code quality of non-accessibility related code, 
and while figuring out how to write high quality accessibility-related code in the first place.

Automated accessibility checkers, like WAVE (Chrome Extension), SiteImprove, AMP, available as a free
browser extension for Chrome and Firefox should be a component of one's strategy. 
They're useful for finding basic issues with digital accessibility and to check 
for compliance with WCAG (Web Content Accessibility Guidelines), the standard guidelines of web accessibility. 
But compliance with the standards doesn't guarantee that your site is usable for people with disabilities.

Automated tools:

* WAVE
* SiteImprove
* AMP
* ChromeVox
* VoiceOver
* JAWS
* ZoomText

Testing by actually going through the site using tools an accessibility user would use (like screen readers e.g. 
ChromeVox, VoiceOver, JAWS, ZoomText) would give you the highest fidelity test but also cost the most time-wise.

Some basic conditions of accessibility are: 

- Use HTML logically not for style (h1, h2, ...), rely on CSS for styling
- Build the interface such that it can be entirely navigated by keyboard (such as by tab)
- Ensure all images (including glyphicons) have alt text
- Use aria labels

Resources:

- A federal government guide to accessibility: https://pages.18f.gov/accessibility/index.html
- An easy checklist to go over: https://pages.18f.gov/accessibility/checklist/
- Auto html checker: http://squizlabs.github.io/HTML_CodeSniffer/


Some anecdotes from Mark Pilgrim's free online book, "Dive into Accessibility":

- About 10% of the population use the internet with readers that are unable to process javascript. Don't use javascript to power things without an alternative.
- Use real links, not javascript powered redirects e.g. "javascript:link"
- Keyboard strokes like Tab, arrow keys, spacebar, and enter can be used to select and navigate webpage/webforms.
- HTML pages are titled and language is specified, as readers use this to interpret the text
- No new windows are opened e.g. "target=_blank", since this doesn't preserve navigation history (back button doesn't take you back to previous page)
- The Tab key should provide focus to the widget as a whole. For example, tabbing to a menu bar should put focus on the menu's first elem.
- The arrow keys should allow for selection or navigation within the widget. For example, using the left and right arrow keys should move focus to the previous and next menu items.
- When the widget is not inside a form, both the Enter and Spacebar keys should select or activate the control.
- Within a form, the Spacebar key should select or activate the control, while the Enter key should submit the form's default action.
- If in doubt, mimic the standard desktop behavior of the control you are creating.
