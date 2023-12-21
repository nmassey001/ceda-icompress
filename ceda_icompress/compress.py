import numpy as np
import time
from datetime import datetime

from ceda_icompress.BitManipulation.bitshave import BitShave
from ceda_icompress.BitManipulation.bitgroom import BitGroom
from ceda_icompress.BitManipulation.bitset import BitSet
from ceda_icompress.BitManipulation.bitmask import BitMask

# try:
#     import dask
#     use_threads = True
# except ImportError:
#     use_threads = False

COMPRESSION = 'zlib'    # we could change the compression type at a later date if more
                        # compression types become available in the standard netCDF lib

class Compress:
    """Encapsulated methods for compressing a netCDF file, netCDF variable or
    Numpy array to truncate the information according to the analysis passed
    in."""

    def __init__(self):
        self._analysis = None
        self._ci = None
        self._deflate = None
        self._method = None
        self._conv_int = None
        self._conv_float = None
        self._debug = None
        self._pchunk = None


    def __copy_dim(self, input_dim, output_group):
        """Copy the dimensions verbatim"""
        output_dim = output_group.createDimension(
            dimname = input_dim.name, 
            size = input_dim.size
        )
        return output_dim
    

    def __copy_var(self, input_var, output_group):
        """Copy the variable but change some of the attributes to match those required
        by the compression"""
        # get the fill value
        try:
            mv = input_var.getncattr("_FillValue")
        except AttributeError:
            mv = None
        # determine the chunking
        if input_var.chunking() == 'contiguous':
            chunking = None
        else:
            chunking = input_var.chunking()
        chunking = None

        # what type should we use? If we aren't manipulating the bits then check
        # whether we can convert a float64 to float32 or int64 to int32
        var_type = input_var.dtype

        if input_var.dtype == np.int64 and self.conv_int:
            var_type = np.int32
        elif input_var.dtype == np.float64 and self.conv_float:
            var_type = np.float32

        # create the output variable
        output_var = output_group.createVariable(
            varname = input_var.name,
            datatype = var_type, 
            dimensions = input_var.dimensions,
            compression = COMPRESSION,
            complevel = self.deflate,
            contiguous = False,
            chunksizes = chunking,
            endian = input_var.endian(),
            fill_value = mv,
            chunk_cache = input_var.get_var_chunk_cache()[0]
        )
        # copy the attributes from input_var to output_var
        output_var.setncatts(input_var.__dict__)
        return output_var


    def compress_dataset(self, input_ds, output_ds):
        """Perform the compression on an input Dataset, writing into an already
        open Dataset.
        Args:
            input_ds (netCDF Dataset)  : the Dataset to perform the compression on
            output_ds (netCDF Dataset) : the Dataset to write the compressed data to
        Returns:
            None
        Side Effects:
            output_ds (netCDF Dataset) : data is written to this Dataset
        """
        # the Dataset is itself a group so we can just call compress_group here
        self.compress_group(input_ds, output_ds)


    def compress_group(self, input_group, output_group):
        """Perform the compression on an input Group, writing into an already
        created netCDF Group.
        Args:
            input_group (netCDF Group)  : the Group to perform the compression on
            output_group (netCDF Group) : the Group to write the compressed data to
        Returns:
            None
        Side Effects:
            output_ds (netCDF Group) : data is written to this Group
        """
        # input_group might be a Dataset
        # copy the metadata
        atts = input_group.__dict__
        output_group.setncatts(atts)

        # copy the dimensions
        for dim in input_group.dimensions:
            new_dim = self.__copy_dim(input_group.dimensions[dim], output_group)
        # copy the variables
        for var in input_group.variables:
            input_var = input_group.variables[var]
            output_var = self.__copy_var(input_var, output_group)
            # are we going to manipulate the bits or just copy the data for the variable
            # just created?  This is determined if the variable name is in the list of
            # variables in the analysis
            bit_manipulate = (output_group.name in self.analysis["groups"] and 
                input_var.name in self.analysis["groups"][output_group.name]["vars"])
            if bit_manipulate:
                # get the variable analysis from the analysis dictionary
                Va = self.analysis["groups"][output_group.name]["vars"][input_var.name]
                self.compress_variable(input_var, output_var, Va)
            else:
                output_var[:] = input_var[:]
        # copy all the groups belonging to this group recursively
        for grp in input_group.groups:
            new_group = output_group.createGroup(grp.name)
            self.compress_group(input_group.groups[grp], new_group)


    def compress_variable(self, input_var, output_var, Va):
        """Perform the compression on a netCDF Variable, writing into an already
        created netCDF Variable
        Args:
            input_var (netCDF Variable)  : the Variable to perform the 
                compression on
            output_var (netCDF Variable) : the Variable to write the compressed 
                data to
            Va (dictionary) : analysis data for this variable
        Returns:
            None
        Side Effects:
            output_variable (netCDF Variable) : data is written to this Variable
        """

        # check to see if number of bits to retain are enforced?
        if "retainbits" in Va:
            NSB = Va["retainbits"]
        else:
            NSB = -1

        # get a pointer to the function to use
        if self.method == "bitshave":
            method = BitShave(input_var, NSB, Va, self.ci)
        elif self.method == "bitgroom":
            method = BitGroom(input_var, NSB, Va, self.ci)
        elif self.method == "bitset":
            method = BitSet(input_var, NSB, Va, self.ci)
        elif self.method == "bitmask":
            method = BitMask(input_var, NSB, Va, self.ci)

        # add a description of the compression to the variable
        atts = output_var.__dict__
        atts["compression"] = (
            f"ceda-icompress: keepbits: {method.NSB}, "
            f"method: {method.method}, "
            f"bitmask: {method.mask:<032b}."
        )
        # add to the history of the variable
        nowtime = datetime.now().replace(microsecond=0).isoformat()
        history = (f"{nowtime} altered by ceda-icompress: lossy compression.")
        if "history" in atts:
            atts["history"] += " " + history
        else:
            atts["history"] = history
        output_var.setncatts(atts)

        if self.debug:
            print(
                f"Processing variable: {input_var.name}\n"
                f"    Retained bits  : {method.NSB}\n"
                f"    Bitmask        : {method.mask:<032b}"
            )
        st = time.time()
        # do each individual timestep to prevent memory swapping
        t_dim = -1
        s = []
        dc = 0
        for d in input_var.dimensions:
            dim = output_var.get_dims()[dc]
            if d == "time" or d == "t":
                t_dim = dc
                t_len = dim.size
                # create the slices
                s.append(slice(0,1,1))
            else:
                s.append(slice(0,dim.size,1))
            dc += 1

        pc = self.pchunk
        if t_dim == -1:
            # copy the data from input_var to output_var, doing the bitshave or bitgroom
            # no time dimension so do all the variable at once
            output_var[:] = method.process(input_var[:])
        else:
            for t in range(0, t_len, pc):
                # modify the slice for the time dimensions
                s[t_dim] = slice(t,t+pc,1)
                output_var[s] = method.process(input_var[s])
        ed = time.time()
        if self.debug:
            print("    Time taken     :", ed-st)


    @property
    def analysis(self):
        return self._analysis
    @analysis.setter
    def analysis(self, val):
        self._analysis = val

    @property
    def ci(self):
        return self._ci
    @ci.setter
    def ci(self, val):
        self._ci = val
    
    @property
    def deflate(self):
        return self._deflate
    @deflate.setter
    def deflate(self, val):
        self._deflate = val

    @property
    def method(self):
        return self._method
    @method.setter
    def method(self, val):
        self._method = val

    @property
    def conv_int(self):
        return self._conv_int
    @conv_int.setter
    def conv_int(self, val):
        self._conv_int = val

    @property
    def conv_float(self):
        return self._conv_float
    @conv_float.setter
    def conv_float(self, val):
        self._conv_float = val

    @property
    def debug(self):
        return self._debug
    @debug.setter
    def debug(self, val):
        self._debug = val

    @property
    def pchunk(self):
        return self._pchunk
    @pchunk.setter
    def pchunk(self, val):
        self._pchunk = val
