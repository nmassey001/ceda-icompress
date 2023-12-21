
import numpy as np
import time
from datetime import datetime
import os.path

from ceda_icompress.InfoMeasures.bitinformation import bitinformation
from ceda_icompress.InfoMeasures.getsigmanexp import getsigmanexp
from ceda_icompress.CLI import CIC_FILE_FORMAT_VERSION

try:
    import dask
    use_threads = True
except ImportError:
    use_threads = False

class Analyse:
    """Encapsulated methods for analysing a netCDF file, netCDF variable or
    Numpy array to determine the information content and produce an analysis
    dictionary."""

    def __init__(self):
        self._time_start = None
        self._time_end = None
        self._axis = None
        self._level = None
        self._debug = False
        self._threads = 1

    
    def from_dataset(self, dataset, groups=None, vars=None):
        """Perform the analysis on a netCDF dataset that has already been opened
        (using netCDF4.Dataset).
        Args:
            dataset (netCDF Dataset) : the dataset to perform the analysis on.
            groups (list) : list of group names to perform the analysis on.
               If None (default) then analyse all groups.
            vars (list) : list of var names to perform the analysis on.
               If None (default) then analyse all variables
        Returns:
            (Dict) : Dataset information dictionary
        """
        # Determine which subset of groups to work on
        if groups is None:
            # get all the groups in the dataset
            grps = [dataset.groups[g] for g in dataset.groups]
            # append the dataset (which is derived from a group)
            grps.append(dataset)
        else:
            # get the groups (that are in the list)
            try:
                grps = [dataset.groups[g] for g in groups]
            except KeyError as e:
                raise KeyError(f"Group not found: {e.args[0]}")

        # build the 
        # loop over all the selected groups and add to the analysis dictionary
        analysis_dict = {
            "Analysis" : "BitInformation",
            "date" : datetime.now().isoformat(),
            "file" : os.path.abspath(dataset.filepath()),
            "groups" : {},
            "version" : CIC_FILE_FORMAT_VERSION,
        }
        for g in grps:
            grp_dict = self.from_group(g, vars)
            analysis_dict["groups"][g.name] = grp_dict

        return analysis_dict


    def from_group(self, group, vars=None):
        """Perform the analysis on a netCDF group that has already been opened
        (using netCDF4.Dataset).
        Args:
            group (netCDF Dataset) : the group to perform the analysis on.
            vars (list) : list of var names to perform the analysis on.
               If None (default) then analyse all variables
        Returns:
            (Dict) : Group information dictionary
        """
        # Determine which subset of variables to work on
        if vars is None:
            # get all the vars in the group
            vars = [group.variables[v] for v in group.variables]
        else:
            try:
                vars = [group.variables[v] for v in vars]
            except KeyError as e:
                raise KeyError(
                    f"Variable not found: {e.args[0]} in group: {group.name}"
                )
        
        # loop over the selected variables and construct the return dictionary
        grp_dict = {"vars" : {}}
        for v in vars:
            var_dict = self.from_variable(v)
            if var_dict != {}:
                grp_dict["vars"][v.name] = var_dict
        return grp_dict


    def from_variable(self, variable):
        """Perform the analysis on a netCDF variable that has already been 
        opened.
        Args:
            variable (netCDF variable) : the variable to perform the analysis on.
        Returns:
            (Dict) : Variable information Dictionary
        """

        # form the index / slice from the time_start, time_end, level and axis
        s = []

        for d in variable.dimensions:
            if d == "time" or d == "t":
                s.append(slice(self.time_start, self.time_end))
            elif "lev" in d and self.level is not None:
                ls = self.level
                le = ls + 1
                s.append(slice(ls,le))
            else:
                s.append(slice(None))
        if len(s) == 0:
            s = 0
        elif len(s) == 1:
            s = s[0]
        
        # get the data to work on from the variable as a Numpy array
        data = variable[s]

        if self._debug:
            print(
                f"Analysing variable {variable.name}, with shape: {data.shape}"
            )

        # right shift on 64 bit numbers & python types not supported by numpy
        if data.dtype in [
            np.uint64, np.int64, np.float64, '<f8', '>f8', float, int
        ]:
            raise TypeError(
                f"Variable {variable.name} is 64 bit and analysis is not "
                "currently supported for 64 bit numbers."
            )

        # pass the data to the actual analysis and get the bitinformation 
        # dictionary
        bi = self.from_array(data)
        sig, man, exp = getsigmanexp(data.dtype)
        # construct the return variable dictionary
        var_dict = {}
        var_dict["time_start"] = self.time_start
        var_dict["time_end"] = self.time_end
        var_dict["level"] = self.level
        var_dict["axis"] = self.axis
        var_dict["elements"] = int(data.count())
        var_dict["type"] = data.dtype.name
        var_dict["itemsize"] = data.dtype.itemsize          # number of bits
        var_dict["byteorder"] = data.dtype.byteorder
        var_dict["signbit"] = sig
        var_dict["manbit"] = man
        var_dict["expbit"] = exp
        var_dict["bitinfo"] = bi.tolist()

        return var_dict


    def from_array(self, array):
        """Perform the analysis on a Numpy array.
        Args:
            array (Numpy array) : the array to perform the analysis on.
        Returns:
            (Dict) : bitinformation dictionary
        """
        if self._debug:
            print(f"    Computing bit information with {self._threads} threads")
        if self._debug:
            st = time.time()
        # get the bit information / carry out the analysis
        bi = bitinformation(array, self.axis, threads=self._threads)
        if self._debug:
            ed = time.time()
            print("    Bit information time taken: ", ed-st)
        return bi


    @property
    def time_start(self):
        return self._time_start
    @time_start.setter
    def time_start(self, val):
        self._time_start = val

    @property
    def time_end(self):
        return self._time_end
    @time_end.setter
    def time_end(self, val):
        self._time_end = val

    @property
    def axis(self):
        return self._axis
    @axis.setter
    def axis(self, val):
        self._axis = val

    @property
    def level(self):
        return self._level
    @level.setter
    def level(self, val):
        self._level = val

    @property
    def result(self):
        return self.analysis
    
    @property
    def debug(self):
        return self._debug
    @debug.setter
    def debug(self, val):
        self._debug = val

    @property
    def threads(self):
        return self._threads
    @debug.setter
    def threads(self, val):
        if use_threads:
            self._threads = val
        else:
            self._threads = 1