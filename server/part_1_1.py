#!/usr/bin/env python
# -*- coding: utf-8 -*-


def print_week():
    while True:
        try:

            days = int(raw_input("How many days?"))
            day = int(raw_input("What day of the week the month begins?"))

            weeks = (days + day) / 7  # how many weeks this month
            last_day = (days + day) % 7  # How many days in last week

            if last_day > 0:
                weeks += 1

            print "S  M  T  W  T  F  S"

            print "   " * (day % 7),

            start = day
            date = 1  # The date of month
            for i in range(start, days + day):
                if date >= 10:
                    print "%s" % date,
                else:
                    print "%s " % date,

                if (start+1) % 7 == 0:
                    # End of line
                    print ""

                start += 1
                date += 1

            print ""
        except:
            continue


if __name__ == "__main__":
    print_week()