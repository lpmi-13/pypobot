import re

def parsefile(original_array, form, correction_form):

    correction_array = []
    correction_array.extend(original_array)

    for line in correction_array:
        #iterate through array of lines and do a raw_input prompt
        current_index = correction_array.index(line)

        if (line.find(form) > -1):
            found_at = [m.start() for m in re.finditer(form, line)]
            print('found one')
            suggestion = line.replace(form, correction_form, len(found_at))
            user_input = input('would you like to change: \n\n {} \n\n into \n\n {} ...?\n\n (y/n)'.format(line, suggestion))
            if (user_input is 'y'):
                correction_array[current_index] = suggestion
            else:
                correction_array[current_index] = line
        else:
            correction_array[current_index] = line


    return correction_array
