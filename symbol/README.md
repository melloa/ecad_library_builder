# Symbol Parser

## How to run example script
You need the LM3100 datasheet since this example is hardcoded for this

```
python3 ./example_symbol_parser.py /path/to/pdf/lm3100.pdf
```

## How it works
Currently the implementation is pretty simple. When an object is passed into the parser, the parser:
 1. Finds the largest rectangle in the scene and sets that as the part.
 2. Finds all the characters and merges then into text lines that have x, y location
 3. Adds curves to the Symbol object

 Once the parser finishes it returns a Symbol object. In the example script, a symbol can be passed to the `plot()` function to display it.
