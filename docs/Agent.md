# Agent (Abstract Class)

## Overview
The abstract class is the minimum implementation required for an agent.

If you want to create a particular agent,
you need to make it inherit from this class.

## API

### Abstract Method next_step
#### Detail
The method is given the current number n and returns the next value based on it.
#### Argument
The board argument is given by ndarray with the current board.

#### Return 
The next move must be returned.  
return value is tuple. (ex. (0, 3): 0 is vertical index, 3 is horizontal index)


### Getter agent_number
#### Detail
Get agent number

### Setter agent_number
#### Detail
Set agent number



