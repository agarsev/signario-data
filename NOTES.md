## Tomas falsas

- segundo batch: 09,11,12,44
- después de fix C0039: 01

# Data info

last normal: 13592
last outtake: 9053

# Algo

If we use silence, it moves because interpreter starts drifting. Find a baseline
with a lowpass filter (rolling min).

Use Gaussian Mixture model with two components (silence, speech). Cut at the
middle.
