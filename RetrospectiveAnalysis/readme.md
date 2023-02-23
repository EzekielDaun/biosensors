# Retrospective Analysis GUI Alpha

## Setup

Python version >= 3.10

### Windows 10/11

#### Install Python

```shell
winget install --id Python.Python.3.11
```
#### Install Dependencies
- Right click `install-dependencies.ps1`, select `Run with PowerShell`. Answer `Y` if prompted.
- RIght click and run `retrospective-analysis.ps1` in the same method to start the GUI.
### macOS 12 

```shell
brew install python@3.11
```

And follow the brew output (if there is one) to set Python 3.11 into your path.

#### Virtual Environment (Recommended, Optional)

1. Clone this repo and navigate to this folder.
2. Find out the correct command to call Python 3.11. On \*nix platforms, use `which python`.
3. Create a virtual environment by:
   ```shell
   python -m venv .venv
   ```

Then activate the virtual environment.

Official tutorial for the [virtual environment](https://docs.python.org/3/tutorial/venv.html).

#### Dependencies

If using a virtual environment, activate it. Double-check that the commands are calling the right binaries.

```shell
pip install -r requirements.txt
```

## Deployment

[Qt for Python Deployment](https://doc.qt.io/qtforpython-6/deployment.html#deployment-guides)

We tried Nuitka in 2022 summer. The compiled executable is somewhat unstable.

## Usage

```shell
python retrospective_analysis_gui.pyw
```

1. In the menubar, click `File`->`Open Folder` or `ctrl/⌘+O`
2. Select the folder containing the data files
3. Specify analyzer parameters and click `Load`
4. (Optional) In `(Optional) Plot Spectrograms`, select power channels and proper parameters, then click `Spectrogram`
5. Select power channels and click `Start Track`
6. Once the results show up, use the tab to navigate through power channels.
7. If necessary, manually adjust the traces:
   1. Select the trace (Trace1 Time xx-xx) in the combo box
   2. Adjust the offset by multiples of FSR or any arbitrary number in the spinboxes
8. In the `Plot` block, push buttons for various kinds of plots **for this channel only**. Check `Auto-Save` to save the plots in the selected folder when clicking those buttons
9. Assign an assay name to this channel in the `Assay` block
10. Click `Save Results` to save all the fitted peaks in `peaks.mat`, all traces in `peak_shifts.mat`, and the overlaid and grouped traces will be popped up (**This figure will not be saved automatically**)

## FAQ

- Peak tracking raises an error / never stops
  - Please first check the spectrograms in each channel. And only track the channels with resonance peaks.
- There are invisible trace sections
  - This is usually due to the trace containing only a single data point. Try shifting a few FSRs and check the overlay result.
- Curve fitting exceeds iteration limits
  - Try to re-run another time. If the error still exists, try running it on another PC.
  - This error was seen for data from detector 5 in the binding assay of Spike Protein Assay Trial 4 ran in October 2022. More details can be found in the experimental summary of this experiment on the Biosensor Microfluidic Subgroup Google Drive.

## Contribute

If you find (or believe that it is) a critical bug in this project, please submit an [issue](https://github.com/SiEPIC/biosensors/issues).

If you are not sure about how to use a feature or have any suggestions or ideas for the project, feel free to start a [discussion](https://github.com/SiEPIC/biosensors/discussions).

### Develop Notes

- [Type Hints](https://peps.python.org/pep-0585/)

  Although Python is a dynamically typed language, it is still possible to use type hints for better clarity. With type hint, IDE/editor will also have better support for auto-completion and linting.

- Code formatter

  Although it's not a must to use a formatter, if your cooperator is using a formatter, when they are modifying your unformatted code, they would either produce a huge git `diff` or have to make a separate formatting commit. Either will corrupt the git `blame` history.

  This project is using [black](https://black.readthedocs.io/en/stable/integrations/editors.html) with the default setting.

- PySide/PyQt

  This project is using PySide6 due to its LGPL license. (PyQt is under GPLv3 or commercial license.) But due to historical reasons, you may find more resources for PyQt. PySide and PyQt are 99% identical in usage, so the resources for PyQt are usually applicable to PySide as well.

  [Get Started with PySide](https://doc.qt.io/qtforpython-6/index.html)

  Most widgets are designed by `pyside6-designer` and converted to Python files by `pyside6-uic`. See [official tutorials](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/uifiles.html) for guidance on how to use them. For creating signals and slots, currently, this project is using a mixed way of either creating them in designer or directly in code. Either way is fine, but it's preferred to be consistent within one module/widget/window unless the function has to be implemented in one specific way.

- Pythonic, iterator, functional programming (FP) and parallelism

  I like one concept in FP rather than `Pythonic`, that FP tries to avoid using temporary variables and instead uses `lambda` and `map` to describe the operation on the data.

  For example, do a calculation on each of the elements in an array and collect the result:

  ```C
  /* C */
  int results[];
  ...
  for(int index=0; index < items.length; index++) {
     results[index] = calc(items[index]);
  }
  ```

  ```Python
  # Pythonic
  results = [calc(x) for x in items]

  # FP
  results = map(lambda x: calc(x), items)
  ```

  But say, if each element is a list of data, and you want to first filter out some lists, then flatten the nested list, and want the calculation to be applied on every 2 adjacent elements ([sliding window](https://www.geeksforgeeks.org/window-sliding-technique/)).

  ```Python
  # Pythonic
  results = [x for xs in items if is_good(xs) for x in xs] # this can only do the filtering and flatten
                                                           # how to make a sliding window in a Pythonic way?

  # FP
  from itertools import pairwise
  results = map(calc2, pairwise(sum(filter(is_good, items),[])))
  ```

  I would prefer the FP way for better clarity. Just read in reverse order. We can see that the `items` are first filtered, then summed (connected) in a list and paired, then mapped by the calculation function.

  The `pairwise` iterator is from the [itertools](https://docs.python.org/3/library/itertools.html#module-itertools) module. There are also handy iterators such as `product`, `combinations` and `permutations`. Have a look at them.

  The FP style is also friendly to parallelism in most cases. The following example uses a process pool to do the same calculation in parallel.

  ```Python
  from multiprocessing import Pool
  with Pool(processes=4) as pool:
      results = pool.map(calc2, pairwise(sum(filter(is_good, items),[])))
  ```
