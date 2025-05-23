#ifndef VERSION_826_H
#define VERSION_826_H

// VERSION INFO ///////////////////////////////////////////////////////////////////


// ********** UPDATE EVERY RELEASE ***********

#define S826_VERSION_MAJOR      3
#define S826_VERSION_MINOR      4
#define S826_VERSION_BUILD      11

#define S826_DLL_VERTEXT  "3.4.11"


// *******************************************
// Ver 3.0.0 -  support added for flat register address space in revB boards w/v.0.0.64 or higher fpga.
// Ver 3.1.0 -  support for new revision of board.
// Ver 3.2.0 -  eliminate need for CalibrateEnable shunt to installed when not calibrating.
//              added new snapshot reason codes (requires fpga v.0.0.66 or higher).
// Ver 3.3.0 -  added debounce filter functions for counters and gpios (requires fpga v.0.0.69 or higher).
// Ver 3.3.1 -  fixed bug that causes unhandled exception in AdcDataCopy() when *timestamps==NULL.
// Ver 3.3.2 -  added local bus error detection upon system open.
// Ver 3.3.3 -  fixed bug that caused setpoint returned by DacRead to sometimes differ by 1 from last written value.
// Ver 3.3.4 -  fixed bug where invalid counter mode not checked.
// Ver 3.3.5 -  fixed bug that caused Open problem with 2 or more boards at non-consecutive or non-zero-based board numbers.
// Ver 3.3.6 -  fixed multi-thread issue where wait count would block until one thread exits.
// Ver 3.3.7 -  fixed multi-thread issue
// Ver 3.3.8-3.3.10 - miscellaneous bug fixes
// Ver 3.4.1-3.4.11 - Support for RevD boards with AD8251
#endif
