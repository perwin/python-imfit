'''
Created on Sep 18, 2013

@author: andre
'''
from copy import copy, deepcopy


__all__ = ['SimpleModelDescription', 'ModelDescription',
           'ParameterDescription', 'FunctionDescription', 'FunctionSetDescription']

################################################################################

class ParameterDescription(object):
    def __init__(self, name, value, limits=None, fixed=False):
        self._name = name
        self.setValue(value, limits, fixed)
        
    
    @property
    def name(self):
        '''
        The label of the parameter. Example: ``'x0'``, ``'I_e'``.
        '''
        return self._name
    
    
    def setValue(self, value, limits=None, fixed=False):
        '''
        Set the value and constraints to the parameter.
        
        Parameters
        ----------
        value : float
            Value of the parameter.
        
        limits : tuple of floats, optional
            Lower and upper limit of the parameter.
            Default: ``None`` (no limits).
            
        fixed : bool, optional
            Flag the parameter as fixed. Default: ``False``.
        '''
        if limits is not None:
            if value < limits[0]:
                limits[0] = value 
            elif value > limits[1]:
                limits[1] = value
        self.value = value
        self.fixed = fixed
        # FIXME: What does happen when there's only one limit?
        self.limits = limits
        
    
    def setTolerance(self, tol):
        '''
        Set the limits using a tolerance fraction value. For example,
        a tolerance of ``0.2`` for a property of value ``1.0`` sets
        the limits to ``[0.8, 1.2]``. 
        
        Parameters
        ----------
        tol : float
            Tolerance of the property.
            Must lie between ``0.0`` and ``1.0``.
        '''
        if tol > 1.0 or tol < 0.0:
            raise Exception('Tolerance must be between 0.0 and 1.0.')
        self.limits = (self.value * (1 - tol), self.value * (1 + tol))
    
    
    def setLimitsRel(self, i1, i2):
        '''
        Set the limits using relative intervals. The limits
        will be ``[value - i1, value + i2]
        
        Parameters
        ----------
        d1 : float
            Lower limit interval.

        d1 : float
            Upper limit interval.
        '''
        if i1 < 0.0 or i2 < 0.0:
            raise Exception('Limit intervals must be positive.')
        self.setLimits(self.value - i1, self.value + i2)
    
    
    def setLimits(self, v1, v2):
        '''
        Set the limits using absolute values.
        
        Parameters
        ----------
        v1 : float
            Lower limit.

        v1 : float
            Upper limit.
        '''
        if v1 >= v2:
            raise Exception('v2 must be larger than v1.')
            if v1 > self.value:
                v1 = self.value
            elif v2 < self.value:
                v2 = self.value
        self.limits = (v1, v2)
        print 'set limits', self.limits
    
    
    def __str__(self):
        if self.fixed:
            return '%s    %f     fixed' % (self.name, self.value)
        elif self.limits is not None:
            return '%s    %f     %f,%f' % (self.name, self.value, self.limits[0], self.limits[1])
        else:
            return '%s    %f' % (self.name, self.value)
            
################################################################################

class FunctionDescription(object):
    def __init__(self, func_type, name=None, parameters=None):
        if name is None:
            name = func_type
        self.funcType = func_type
        self.name = name
        self._parameters = []
        if parameters is not None:
            for p in parameters:
                self.addParameter(p)
        
        
    def addParameter(self, p):
        if not isinstance(p, ParameterDescription):
            raise ValueError('p is not a Parameter object.')
        self._parameters.append(p)
        
    
    def parameterList(self):
        '''
        A list of the parameters composing this function.
        
        Returns
        -------
        param_list : list of :class:`ParameterDescription`
            List of the parameters.
        '''
        return [p for p in self._parameters]


    def __str__(self):
        lines = []
        lines.append('FUNCTION %s # %s' % (self.funcType, self.name))
        lines.extend(str(p) for p in self._parameters)
        return '\n'.join(lines)

    
    def __getattr__(self, attr):
        return self[attr]
    
    
    def __getitem__(self, key):
        if not isinstance(key, str):
            raise KeyError('Parameter must be a string.')
        for p in self._parameters:
            if key == p.name:
                return p
        raise KeyError('Parameter %s not found.' % key)
    

    def __deepcopy__(self, memo):
        f = FunctionDescription(self.funcType, self.name)
        f._parameters = [copy(p) for p in self._parameters]
        return f

################################################################################

class FunctionSetDescription(object):
    def __init__(self, name, functions=None):
        self.name = name
        self.x0 = ParameterDescription('X0', 0.0)
        self.y0 = ParameterDescription('Y0', 0.0)
        self._functions = []
        if functions is not None:
            for f in functions:
                self.addFunction(f)
        
        
    def addFunction(self, f):
        '''
        Add a function created using :func:`function_description`.
        
        Parameters
        ----------
        f : :class:`FunctionDescription`.
            Function description to be added to the function set.
        '''
        if not isinstance(f, FunctionDescription):
            raise ValueError('func is not a Function object.')
        if self._contains(f.name):
            raise KeyError('Function named %s already exists.' % f.name)
        self._functions.append(f)
    
    
    def _contains(self, name):
        for f in self._functions:
            if f.name == name:
                return True
        return False
    
    
    def functionList(self):
        '''
        A list of the function types composing this function set.
        
        Returns
        -------
        param_list : list of strings
            List of the function types.
        '''
        return [f.funcType for f in self._functions]
    
    
    def parameterList(self):
        '''
        A list of the parameters composing this function set.
        
        Returns
        -------
        param_list : list of :class:`ParameterDescription`
            List of the parameters.
        '''
        params = []
        params.append(self.x0)
        params.append(self.y0)
        for f in self._functions:
            params.extend(f.parameterList())
        return params
    
    
    def __str__(self):
        lines = []
        lines.append(str(self.x0))
        lines.append(str(self.y0))
        lines.extend(str(f) for f in self._functions)
        return '\n'.join(lines)
    
    def __getattr__(self, attr):
        return self[attr]
    
    
    def __getitem__(self, key):
        if not isinstance(key, str):
            raise KeyError('Function must be a string.')
        for f in self._functions:
            if key == f.name:
                return f
        raise KeyError('Function %s not found.' % key)
    
    
    def __deepcopy__(self, memo):
        fs = FunctionSetDescription(self.name)
        fs.x0 = copy(self.x0)
        fs.y0 = copy(self.y0)
        fs._functions = deepcopy(self._functions, memo)
        return fs
        
################################################################################
        
class ModelDescription(object):
    
    def __init__(self, function_sets=None, options={}):
        self.options = {}
        self.options.update(options)
        self._functionSets = []
        if function_sets is not None:
            for fs in function_sets:
                self.addFunctionSet(fs)


    @classmethod
    def load(cls, fname):
        '''
        Creates a model description from a file. The syntax is the same
        as the imfit config file.
        
        Parameters
        ----------
        fname : string
            Path to the model description file.
            
        Returns
        -------
        model : :class:`ModelDescription`
            The model description.
        
        See also
        --------
        parse_config_file
        '''
        from .config import parse_config_file
        return parse_config_file(fname)
    
    
    def addFunctionSet(self, fs):
        '''
        Add a function set to the model description.
        
        Parameters
        ----------
        fs : :class:`FunctionSetDescription`
            Function set description instance.
        '''
        if not isinstance(fs, FunctionSetDescription):
            raise ValueError('fs is not a FunctionSet object.')
        if self._contains(fs.name):
            raise KeyError('FunctionSet named %s already exists.' % fs.name)
        self._functionSets.append(fs)
    
    
    def _contains(self, name):
        for fs in self._functionSets:
            if fs.name == name:
                return True
        return False
    
    
    def functionSetIndices(self):
        '''
        Internal function.
        
        Returns the indices in the full parameters list such that
        imfit can split the parameters for in the function sets.
        '''
        indices = [0]
        for i in xrange(len(self._functionSets) - 1):
            indices.append(len(self.functionSets[i].functions))
        return indices
        
        
    def functionList(self):
        '''
        List of the function types composing this model, as strings.

        Returns
        -------
        func_list : list of string
            List of the function types.
        '''
        functions = []
        for function_set in self._functionSets:
            functions.extend(function_set.functionList())
        return functions
    

    def parameterList(self):
        '''
        A list of the parameters composing this model.
        
        Returns
        -------
        param_list : list of :class:`ParameterDescription`
            List of the parameters.
        '''
        params = []
        for function_set in self._functionSets:
            params.extend(function_set.parameterList())
        return params


    def __str__(self):
        lines = []
        for k, v in self.options.items():
            lines.append('%s    %f' % (k, v))
        lines.extend(str(fs) for fs in self._functionSets)
        return '\n'.join(lines)
        

    def __getattr__(self, attr):
        return self[attr]
    
    
    def __getitem__(self, key):
        if not isinstance(key, str):
            raise KeyError('FunctionSet must be a string.')
        for fs in self._functionSets:
            if key == fs.name:
                return fs
        raise KeyError('FunctionSet %s not found.' % key)
    
    
    def __deepcopy__(self, memo):
        model = type(self)()
        model._functionSets = deepcopy(self._functionSets, memo)
        return model
        
################################################################################


class SimpleModelDescription(ModelDescription):
    '''
    Simple model with only one function set.
    
    Returns
    -------
    model : :class:`SimpleModelDescription`
        Empty model description.
        
    Examples
    --------
    TODO: Add example of SimpleModelDescription.
    
    See also
    --------
    ModelDescription
    '''

    def __init__(self, inst=None):
        super(SimpleModelDescription, self).__init__()
        if isinstance(inst, ModelDescription):
            if len(inst._functionSets) != 1:
                raise ValueError('Original model must have only one function set.')
            self.addFunctionSet(copy(inst._functionSets[0]))
        elif inst is None:
            self.addFunctionSet(FunctionSetDescription('fs'))
        else:
            raise ValueError('Invalid type: %s' % type(inst))
        
        
    @property
    def x0(self):
        '''
        X coordinate of the center of the model.
        Instance of :class:`ParameterDescription`.
        '''
        return self._functionSets[0].x0
        

    @property
    def y0(self):
        '''
        Y coordinate of the center of the model.
        Instance of :class:`ParameterDescription`.
        '''
        return self._functionSets[0].y0
    

    def addFunction(self, f):
        '''
        Add a function created using :func:`function_description`.
        
        Parameters
        ----------
        f : :class:`FunctionDescription`.
            Function description to be added to the model.
        '''
        self._functionSets[0].addFunction(f)
        
        
    def __getattr__(self, attr):
        return self._functionSets[0][attr]
