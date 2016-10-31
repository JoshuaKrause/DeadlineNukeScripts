NukeToNuke Deadline post-render action script
by Joshua Krause (jkrause@joshuakrause.net)
---------------------------------------------

At my current job, we need to produce two Quicktime movies per VFX shot -- one in sRGB for preview purposes and a final output file in an Alexa colorspace using the DNxHD codec. This is automated by submitting a job that renders frames and attaching this post-render action.

The action does the following:

Create new job submission and job info files for Deadline by extracting details from the initial frame rendering job.

Create a new Nuke file that contains a read node that points to the original frame render and two write nodes that output in the desired formats. This is done by submitting CreateNukeFile.py to the Nuke command line application.

Submits the new file and the new info files to Deadline as a new render.