# Ignore any locally installed files to make builds reproducible
#
# (? is a deliberately chosen, invalid path. Unsetting the environment
# variable or setting it to the empty string would have LaTeX search the
# default texmf directory location, which we can only avoid by using an
# invalid path)
$ENV{"TEXMFHOME"} = "?";

# Reset all search paths
$ENV{"BIBINPUTS"} = "";
$ENV{"BSTINPUTS"} = "";
$ENV{"TEXINPUTS"} = "";

# Only search within the supplied includes directory
ensure_path("BIBINPUTS", "./includes//");
ensure_path("BSTINPUTS", "./includes//");
ensure_path("TEXINPUTS", "./includes//");
