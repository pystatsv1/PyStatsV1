Applied Statistics with Python – Chapter 3
==========================================

Data and Programming (Python-first view)
----------------------------------------

This chapter is the Python companion to the "Data and Programming" chapter
from the R notes. The *statistical* ideas are the same:

* You need a small set of **data types** (numbers, text, booleans).
* You store them in **data structures** (vectors/arrays, matrices, tables).
* You use **programming tools** (control flow + functions) to glue analyses together.

The R book uses R’s vocabulary (vectors, matrices, lists, data frames).
Here we’ll use the Python stack that maps to the same concepts:

* Core Python (built-in types and control flow)
* NumPy (for arrays, vectorization, and linear algebra)
* pandas (for tabular data like R data frames / tibbles)

The goal is not to turn you into a software engineer. The goal is:

*Think “what is the data?” and “what operation am I doing?” and then choose
the Python object that matches that mental model.*


3.1 Data Types
--------------

R has numeric, integer, complex, logical, character. Python has very similar
building blocks:

* ``int`` – integers: ``1``, ``42``, ``-3``
* ``float`` – real numbers (double precision): ``1.0``, ``3.14``, ``-0.001``
* ``complex`` – complex numbers: ``4+2j``
* ``bool`` – logical values: ``True`` or ``False``
* ``str`` – text: ``"a"``, ``"Statistics"``, ``"1 plus 2"``

A few quick parallels:

* R’s ``TRUE`` / ``FALSE`` ↔ Python’s ``True`` / ``False``
* R’s ``NA`` ↔ Python’s ``None`` (missing in general) or ``numpy.nan`` (missing numeric)
* R’s automatic coercion (e.g., mixing numbers and strings in a vector)
  ↔ in Python, lists *can* hold mixed types, but numerical containers
  like NumPy arrays and pandas columns are usually homogeneous.


3.2 Data Structures: R vs Python mental map
-------------------------------------------

R distinguishes between "homogeneous" (everything the same type) and
"heterogeneous" (mixed types). Same idea in Python, just with different names.

===================  =================  ========================
Dimension            Homogeneous (R)    Homogeneous (Python)
===================  =================  ========================
1D                   vector             NumPy ``ndarray`` (1D),
                                        pandas ``Series``
2D                   matrix             NumPy 2D ``ndarray``,
                                        pandas ``DataFrame``
3D+                  array              higher-dim NumPy ``ndarray``
===================  =================  ========================

===================  =================  ========================
Dimension            Heterogeneous (R)  Heterogeneous (Python)
===================  =================  ========================
1D                   list               Python ``list``, ``dict``,
                                        ``dataclass``
2D                   data frame         pandas ``DataFrame``
===================  =================  ========================

We’ll mostly use:

* **Python lists** for small, generic sequences.
* **NumPy arrays** when we mean “numeric vector/matrix.”
* **pandas DataFrames** when we mean “rectangular data with named columns.”


3.2.1 One-dimensional containers: lists, ranges, and NumPy arrays
-----------------------------------------------------------------

Python list: flexible sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the closest analogue to an R "generic" vector (but can hold mixed types):

.. code-block:: python

   x = [1, 3, 5, 7, 8, 9]
   x[0]      # 1 (0-based indexing in Python)
   x[2]      # 5
   x[-1]     # 9 (last element)

Remember: **Python indexes from 0**, not 1. That’s one of the biggest
mental differences from R.


Creating sequences
~~~~~~~~~~~~~~~~~~

R uses ``c()``, ``:`` and ``seq()``. Python equivalents:

.. code-block:: python

   # Explicit list
   x = [1, 3, 5, 7, 8, 9]

   # A sequence of integers (like 1:100 in R)
   y = list(range(1, 101))  # 1, 2, ..., 100

   # A sequence with a step (like seq(1.5, 4.2, by = 0.1))
   import numpy as np

   seq = np.arange(1.5, 4.3, 0.1)  # up to (but not including) 4.3

Repetition
~~~~~~~~~~

R has ``rep()``. In Python:

.. code-block:: python

   ["A"] * 10             # ['A', 'A', ..., 'A']
   x * 3                  # repeats the list x three times

   # with NumPy for numeric work:
   x_arr = np.array(x)
   rep_arr = np.tile(x_arr, 3)  # repeat the vector x three times


Vector length
~~~~~~~~~~~~~

R: ``length(x)``

Python:

.. code-block:: python

   len(x)         # length of a list
   len(x_arr)     # length of a NumPy array


3.2.1.1 Subsetting and slicing
------------------------------

R uses ``x[1]``, ``x[1:3]``, negative indices to drop elements, and logical
vectors. Python has similar ideas but with different syntax.

Indexing by position
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   x = [1, 3, 5, 7, 8, 9]

   x[0]       # 1  (first element)
   x[2]       # 5  (third element)
   x[1:4]     # [3, 5, 7]  (slice: start inclusive, stop exclusive)
   x[:3]      # [1, 3, 5]
   x[3:]      # [7, 8, 9]
   x[-1]      # 9 (last)
   x[-2:]     # [8, 9] (last two)

NumPy arrays support exactly the same slice notation:

.. code-block:: python

   x_arr = np.array(x)
   x_arr[0]      # 1
   x_arr[1:4]    # array([3, 5, 7])


Boolean indexing (logical subsetting)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is where NumPy and pandas line up very nicely with R.

R:

.. code-block:: r

   x[x > 3]
   x[x != 3]

NumPy:

.. code-block:: python

   mask = x_arr > 3          # array([False, False, True, True, True, True])
   x_arr[mask]               # array([5, 7, 8, 9])

   x_arr[x_arr != 3]         # array([1, 5, 7, 8, 9])


3.2.2 Vectorization in Python
-----------------------------

The R chapter emphasises that R is “vectorized”: operations apply to whole
vectors at once. Same idea in the scientific Python stack:

* Pure Python lists: arithmetic is **not** vectorized.
* NumPy arrays and pandas objects: arithmetic **is** vectorized.

Compare:

.. code-block:: python

   x_list = [1, 2, 3, 4, 5]

   # NOT vectorized – this concatenates lists
   x_list + [1]           # [1, 2, 3, 4, 5, 1]

   # Vectorized: use NumPy arrays
   x = np.array([1, 2, 3, 4, 5])

   x + 1                  # array([2, 3, 4, 5, 6])
   2 * x                  # array([ 2,  4,  6,  8, 10])
   2 ** x                 # powers, elementwise
   np.sqrt(x)
   np.log(x)

Same mental model as in R:

*“If I apply a numeric function to a whole vector, I get a vector back.”*


Length recycling vs broadcasting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In R, ``x + y`` can silently **recycle** the shorter vector and even warn if
lengths don’t match nicely.

In NumPy:

* Shapes must be **compatible** for broadcasting.
* Shape mismatch gives an error instead of a warning (which is usually safer).

Example:

.. code-block:: python

   x = np.array([1, 3, 5, 7, 8, 9])
   y = np.arange(1, 61)

   x + y      # works: NumPy broadcasts x along y’s length (6 divides 60)

   # If shapes truly don't match, you'll get a ValueError instead of a “silent” recycle.


3.2.3 Logical operators
-----------------------

R operators: ``<``, ``>``, ``<=``, ``>=``, ``==``, ``!=``, ``!``, ``&``, ``|``.

Python has very similar operators:

.. code-block:: python

   x = np.array([1, 3, 5, 7, 8, 9])

   x > 3        # array([False, False,  True,  True,  True,  True])
   x < 3        # array([ True, False, False, False, False, False])
   x == 3       # array([False,  True, False, False, False, False])
   x != 3       # array([ True, False,  True,  True,  True,  True])

A few important notes:

* For **NumPy arrays**, use ``&`` and ``|`` for elementwise AND/OR, with
  parentheses:

  .. code-block:: python

     (x > 3) & (x < 8)    # both conditions
     (x == 3) | (x == 9)  # either condition

* For pure Python booleans (not arrays), use ``and`` / ``or``:

  .. code-block:: python

     (3 < 4) and (42 > 13)

Counting and coercion
~~~~~~~~~~~~~~~~~~~~~

R shows that logical values act like 0/1 in numeric calculations (``sum(x > 3)``).
Same in Python/NumPy:

.. code-block:: python

   mask = x > 3
   mask           # array([False, False,  True,  True,  True,  True])

   mask.sum()     # 4 (True acts like 1, False like 0)
   np.sum(mask)   # also 4

   mask.astype(int)   # array([0, 0, 1, 1, 1, 1])


3.2.4 Matrices and linear algebra (NumPy)
-----------------------------------------

R uses ``matrix()``, ``%*%``, ``t()``, ``solve()``, ``diag()`` and friends.
In Python, these live in NumPy:

Creating matrices
~~~~~~~~~~~~~~~~~

.. code-block:: python

   x = np.arange(1, 10)          # 1..9
   X = x.reshape(3, 3, order="F")  # like R’s column-major matrix()
   X

   # array([[1, 4, 7],
   #        [2, 5, 8],
   #        [3, 6, 9]])

   Y = x.reshape(3, 3, order="C")  # row-wise (byrow = TRUE in R)
   Y

   Z = np.zeros((2, 4))           # 2x4 matrix of zeros

Subsetting
~~~~~~~~~~

.. code-block:: python

   X[0, 1]     # element in first row, second column  (4)
   X[0, :]     # first row
   X[:, 1]     # second column
   X[1, [0, 2]]  # row 2, columns 1 and 3


Matrix operations
~~~~~~~~~~~~~~~~~

Elementwise operations:

.. code-block:: python

   X + Y
   X - Y
   X * Y    # elementwise product
   X / Y    # elementwise division

Matrix multiplication and linear algebra:

.. code-block:: python

   # matrix multiplication (like R's %*%)
   X @ Y
   np.matmul(X, Y)

   # transpose
   X_T = X.T

   # identity and diagonal matrices
   np.eye(3)          # 3x3 identity
   np.diag([1, 2, 3]) # diagonal with 1,2,3 on the diagonal

   # inverse (if invertible)
   Z = np.array([[9, 2, -3],
                 [2, 4, -2],
                 [-3, -2, 16]])

   Z_inv = np.linalg.inv(Z)

   Z_inv @ Z
   # approximately the identity matrix

Floating point equality
~~~~~~~~~~~~~~~~~~~~~~~

R uses ``all.equal`` to compare floating-point matrices. NumPy equivalent:

.. code-block:: python

   np.allclose(Z_inv @ Z, np.eye(3))   # True
   (Z_inv @ Z == np.eye(3)).all()      # often False due to tiny round-off


Dot product and outer product
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

R uses ``a_vec %*% b_vec`` and ``a_vec %o% b_vec``; also ``crossprod``.

Python:

.. code-block:: python

   a_vec = np.array([1, 2, 3])
   b_vec = np.array([2, 2, 2])

   # Inner (dot) product
   a_vec @ b_vec           # 12
   np.dot(a_vec, b_vec)    # 12

   # Outer product
   np.outer(a_vec, b_vec)

   # “crossprod(X, Y)” (X^T Y) in NumPy:
   C_mat = np.array([[1, 2, 3],
                     [4, 5, 6]])
   D_mat = np.array([[2, 2, 2],
                     [2, 2, 2]])

   C_mat.T @ D_mat    # like crossprod(C_mat, D_mat)
   np.allclose(C_mat.T @ D_mat, C_mat.T.dot(D_mat))


3.2.5 Heterogeneous containers: lists and dicts
-----------------------------------------------

The R chapter introduces **lists** as "one-dimensional containers that can hold
anything": vectors, matrices, functions, etc.

In Python we have:

* ``list`` – ordered sequence (can be mixed types)
* ``dict`` – mapping from names to values (key–value store)

An R list like:

.. code-block:: r

   ex_list = list(
     a = c(1, 2, 3, 4),
     b = TRUE,
     c = "Hello!",
     d = function(arg = 42) { print("Hello World!") },
     e = diag(5)
   )

could be represented roughly as:

.. code-block:: python

   def say_hello(arg=42):
       print("Hello World!")

   ex_dict = {
       "a": np.array([1, 2, 3, 4]),
       "b": True,
       "c": "Hello!",
       "d": say_hello,
       "e": np.diag(np.arange(1, 6))
   }

Accessing elements:

.. code-block:: python

   ex_dict["e"]      # matrix
   ex_dict["a"]      # array
   ex_dict["d"](arg=1)


3.2.6 Tabular data: pandas DataFrames
-------------------------------------

R’s data frame / tibble ↔ Python’s pandas ``DataFrame``.

Minimal example:

.. code-block:: python

   import pandas as pd

   example_data = pd.DataFrame({
       "x": [1, 3, 5, 7, 9, 1, 3, 5, 7, 9],
       "y": ["Hello"] * 9 + ["Goodbye"],
       "z": [True, False] * 5
   })

   example_data
   example_data.head()      # first rows
   example_data.info()      # structure, types
   example_data.shape       # (n_rows, n_cols)
   example_data.columns     # column names

Reading from CSV (similar to ``read_csv`` in R):

.. code-block:: python

   cars = pd.read_csv("data/example-data.csv")

   # glimpse the data
   cars.head(10)
   cars.info()

Subsetting rows and columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like R:

.. code-block:: python

   # single column as a Series
   example_data["x"]

   # multiple columns as a DataFrame
   example_data[["x", "y"]]

   # Boolean filter: “fuel efficient cars”
   mask = example_data["x"] > 5
   example_data[mask]

   # Equivalent to subset(mpg, subset = hwy > 35, select = c("manufacturer", "model", "year")):
   mpg = cars  # imagine we loaded the mpg data
   mpg[mpg["hwy"] > 35][["manufacturer", "model", "year"]]

You can also use ``query`` for more R-like syntax:

.. code-block:: python

   mpg.query("hwy > 35")[["manufacturer", "model", "year"]]


3.3 Programming Basics in Python
--------------------------------

Now we connect data structures with basic programming tools:
control flow and functions.


3.3.1 Control flow
------------------

If / elif / else
~~~~~~~~~~~~~~~~

R:

.. code-block:: r

   if (x > y) {
     # ...
   } else {
     # ...
   }

Python:

.. code-block:: python

   x = 1
   y = 3

   if x > y:
       z = x * y
       print("x is larger than y")
   else:
       z = x + 5 * y
       print("x is less than or equal to y")

There is also a short expression form (similar spirit to ``ifelse`` for scalars):

.. code-block:: python

   result = 1 if 4 > 3 else 0     # 1


Vectorized “if” with NumPy/pandas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

R’s ``ifelse(condition, value_if_true, value_if_false)`` is used for vectors.

In Python we use ``np.where`` or pandas methods:

.. code-block:: python

   fib = np.array([1, 1, 2, 3, 5, 8, 13, 21])
   np.where(fib > 6, "Foo", "Bar")
   # array(['Bar', 'Bar', 'Bar', 'Bar', 'Bar', 'Foo', 'Foo', 'Foo'], dtype='<U3')

For pandas Series:

.. code-block:: python

   mpg["label"] = np.where(mpg["hwy"] > 35, "Efficient", "Regular")


For loops vs vectorization
~~~~~~~~~~~~~~~~~~~~~~~~~~

The R chapter shows that explicit loops are often replaced by vectorized code.

Same in Python:

.. code-block:: python

   # Loop version
   x = [11, 12, 13, 14, 15]
   for i in range(len(x)):
       x[i] = x[i] * 2

   # Vectorized version with NumPy
   x_arr = np.array([11, 12, 13, 14, 15])
   x_arr = x_arr * 2


3.3.2 Defining functions
------------------------

Basic structure
~~~~~~~~~~~~~~~

R:

.. code-block:: r

   standardize = function(x) {
     (x - mean(x)) / sd(x)
   }

Python:

.. code-block:: python

   import numpy as np

   def standardize(x: np.ndarray) -> np.ndarray:
       """
       Standardize a numeric vector/array:
       subtract the mean and divide by the sample standard deviation.
       """
       m = x.mean()
       s = x.std(ddof=1)   # ddof=1 for sample SD (like R's sd)
       return (x - m) / s

Test it:

.. code-block:: python

   sample = np.random.normal(loc=2, scale=5, size=10)
   z = standardize(sample)

   z.mean()      # close to 0
   z.std(ddof=1) # close to 1


Default arguments
~~~~~~~~~~~~~~~~~

R:

.. code-block:: r

   power_of_num = function(num, power = 2) {
     num ^ power
   }

Python:

.. code-block:: python

   def power_of_num(num, power=2):
       return num ** power

   power_of_num(10)                # 100
   power_of_num(num=10, power=2)   # 100
   power_of_num(power=3, num=2)    # 8


Variance example (biased vs unbiased)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The R notes define two forms of variance: unbiased (divide by n−1)
and biased (divide by n).

We can mirror this:

.. code-block:: python

   def sample_variance(x: np.ndarray, biased: bool = False) -> float:
       """
       Compute the variance of x.

       biased = False  -> divide by (n-1)  (unbiased, like R's var)
       biased = True   -> divide by n      (ML / population variance)
       """
       x = np.asarray(x)
       n = x.size
       ddof = 0 if biased else 1
       return x.var(ddof=ddof)

   sample = np.random.normal(size=10)
   sample_variance(sample)            # unbiased (n-1)
   sample_variance(sample, True)      # biased (n)


3.4 What you should take away
-----------------------------

By the end of this chapter (R + Python versions), you should be comfortable with:

* Distinguishing **data types** (int, float, bool, str, complex).
* Choosing an appropriate **data structure**:

  - list vs NumPy array vs pandas DataFrame
  - when you want homogeneity (numeric computation) vs heterogeneity.

* Using **vectorized operations** instead of unnecessary loops:

  - arithmetic on whole arrays
  - logical masks and boolean indexing
  - basic linear algebra with NumPy.

* Writing **small helper functions** with clear arguments and defaults
  to standardize repeated analysis steps.

In later PyStatsV1 chapters, you’ll see these ideas used to:

* build reusable simulation functions,
* manipulate data for case studies,
* and express models in a compact, vectorized way.

If any of the Python code in this chapter feels new, it’s worth
experimenting interactively in a notebook or Python shell:

* create a small vector or DataFrame,
* try out indexing and filtering,
* write a tiny function and call it on real data.

That practice will pay off quickly in the applied chapters.
