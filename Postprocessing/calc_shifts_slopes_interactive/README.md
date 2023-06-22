# Postprocessing with calc_shifts_slopes_interactive.m

`calc_shifts_slopes_interactive.m` was intended to be an interim solution to implement postprocessing analysis of our quantified peak-shift data (quantified using RetrospectiveAnalysis).
The script was designed to quantify two types of data:
1. Peak shifts (comparing the average peak position over a set of measurements before protein binding to that after protein binding).
Peak shifts should be quantified when the sensor is in the same solution (e.g., during PBS wash steps before and after binding) to isolate the effect of bound protein from that of bulk refractive index changes.
2. Stability, via approximation by a linear fit to the peak shift vs. time plots.

Instructions for how to run the script are available on Google Drive [here](https://docs.google.com/document/d/10AL7evmuJRPfRwwFHkrGfg5XB3GPehuFUmTauIewR4Y/edit?usp=sharing).
Example files are available on Google Drive [here](https://drive.google.com/drive/folders/1axrYmjY4yJe66jboki9RJWhfjQZPDVj3?usp=share_link).