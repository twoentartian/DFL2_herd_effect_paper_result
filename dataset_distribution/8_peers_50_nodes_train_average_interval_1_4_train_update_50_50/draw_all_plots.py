import os
import sys

import numpy
import pandas
import matplotlib.pyplot as plt

row = 1
col = 3

folders = ["iid", "non_iid_alpha_0_5", "non_iid_alpha_0_1"]

titles = ["I.I.D.", "non-I.I.D. alpha=0.5", "non-I.I.D. alpha=0.1"]

maximum_tick = 10000
save_name = "dataset_distribution_train_average_interval_1_4"

folder_names_set = set()
for folder_index in range(len(folders)):
    folder = folders[folder_index]
    assert not (folder in folder_names_set)
    folder_names_set.add(folder)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


assert len(folders) == row * col

flag_generate_whole = query_yes_no('do you want to generate the whole figure?')
if flag_generate_whole:
    whole_fig, whole_axs = plt.subplots(row*2, col, figsize=(5*col, 5*row))
    for folder_index in range(len(folders)):
        current_col = folder_index % col
        current_row = folder_index // col

        folder = folders[folder_index]

        subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]
        assert len(subfolders) != 0
        final_accuracy_df = pandas.DataFrame()
        final_weight_diff_df = pandas.DataFrame()
        is_first_dataframe = True
        for each_test_result_folder in subfolders:
            accuracy_file_path = each_test_result_folder + '/accuracy.csv'
            accuracy_df = pandas.read_csv(accuracy_file_path, index_col=0, header=0)
        # print(accuracy_df)

            weight_diff_file_path = each_test_result_folder + '/model_weight_diff.csv'
            weight_diff_df = pandas.read_csv(weight_diff_file_path, index_col=0, header=0)
        # print(weight_diff_df)

            if is_first_dataframe:
                is_first_dataframe = False
                final_accuracy_df = accuracy_df
                final_weight_diff_df = weight_diff_df
            else:
                final_accuracy_df = final_accuracy_df.add(accuracy_df, fill_value=0)
                final_weight_diff_df = final_weight_diff_df.add(weight_diff_df, fill_value=0)
        final_accuracy_df = final_accuracy_df.div(len(subfolders))
        final_weight_diff_df = final_weight_diff_df.div(len(subfolders))
        print(final_accuracy_df)
        print(final_weight_diff_df)

        accuracy_x = final_accuracy_df.index
        accuracy_df_len = len(final_accuracy_df)
        weight_diff_x = final_weight_diff_df.index
        weight_diff_df_len = len(final_weight_diff_df)

        accuracy_axis = whole_axs[current_row*2, current_col]
        weight_diff_axis = whole_axs[current_row*2+1, current_col]

        if maximum_tick >= accuracy_x[len(accuracy_x)-1]:
            end_accuracy_x = len(accuracy_x)-1
        else:
            end_accuracy_x = next(k for k, value in enumerate(accuracy_x) if value > maximum_tick)  # find the end of axis
        for _col in final_accuracy_df.columns:
            accuracy_axis.plot(accuracy_x[0:end_accuracy_x], final_accuracy_df[_col][0:end_accuracy_x], label=_col, alpha=0.75)

        if maximum_tick >= weight_diff_x[len(weight_diff_x)-1]:
            end_weight_diff_x = len(weight_diff_x)-1
        else:
            end_weight_diff_x = next(k for k, value in enumerate(weight_diff_x) if value > maximum_tick)  # find the end of axis
        for _col in final_weight_diff_df.columns:
            if numpy.sum(final_weight_diff_df[_col]) == 0:
                continue
            weight_diff_axis.plot(weight_diff_x[0:end_weight_diff_x], final_weight_diff_df[_col][0:end_weight_diff_x], label=_col, linewidth=2)

        accuracy_axis.grid()
        accuracy_axis.legend(ncol=5)
        if len(final_accuracy_df.columns) > 10:
            accuracy_axis.legend().remove()
        accuracy_axis.set_title('Subplot ' + str(folder_index+1) + 'a-accuracy: ' + titles[folder_index])
        accuracy_axis.set_xlabel('time (tick)')
        accuracy_axis.set_ylabel('accuracy (0-1)')
        accuracy_axis.set_xlim([0, final_accuracy_df.index[end_accuracy_x]])
        accuracy_axis.set_ylim([0, 1])

        weight_diff_axis.grid()
        weight_diff_axis.legend(ncol=4, prop={'size': 8})
        weight_diff_axis.set_title('Subplot ' + str(folder_index+1) + 'b-model weight diff: ' + titles[folder_index])
        weight_diff_axis.set_xlabel('time (tick)')
        weight_diff_axis.set_ylabel('weight diff')
        weight_diff_axis.set_yscale('log')
        weight_diff_axis.set_xlim([0, final_weight_diff_df.index[end_weight_diff_x]])

    whole_fig.tight_layout()
    whole_fig.savefig(save_name + '.pdf')
    whole_fig.savefig(save_name + '.jpg', dpi=800)
    plt.close(whole_fig)

flag_generate_for_each_result = query_yes_no('do you want to draw accuracy graph and weight difference graph for each simulation result?', default="no")
if flag_generate_for_each_result:
    for folder_index in range(len(folders)):
        folder = folders[folder_index]
        subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]
        assert len(subfolders) != 0
        for each_test_result_folder in subfolders:
            print("processing: " + each_test_result_folder)
            accuracy_file_path = each_test_result_folder + '/accuracy.csv'
            accuracy_df = pandas.read_csv(accuracy_file_path, index_col=0, header=0)

            weight_diff_file_path = each_test_result_folder + '/model_weight_diff.csv'
            weight_diff_df = pandas.read_csv(weight_diff_file_path, index_col=0, header=0)

            accuracy_x = accuracy_df.index
            accuracy_df_len = len(accuracy_df)

            weight_diff_x = weight_diff_df.index
            weight_diff_df_len = len(weight_diff_df)

            fig, axs = plt.subplots(2, figsize=(10, 10))
            for col in accuracy_df.columns:
                axs[0].plot(accuracy_x, accuracy_df[col], label=col, alpha=0.75)

            for col in weight_diff_df.columns:
                axs[1].plot(weight_diff_x, weight_diff_df[col], label=col)

            axs[0].grid()
            axs[0].legend(ncol=5)
            axs[0].set_title('accuracy')
            axs[0].set_xlabel('time (tick)')
            axs[0].set_ylabel('accuracy (0-1)')
            axs[0].set_xlim([0, accuracy_df.index[accuracy_df_len - 1]])
            axs[0].set_ylim([0, 1])

            axs[1].grid()
            axs[1].legend()
            axs[1].set_title('model weight diff')
            axs[1].set_xlabel('time (tick)')
            axs[1].set_ylabel('weight diff')
            axs[1].set_yscale('log')
            axs[1].set_xlim([0, weight_diff_df.index[weight_diff_df_len - 1]])

            fig.tight_layout()
            fig.savefig(each_test_result_folder + '/accuracy_weight_diff_combine.pdf')
            fig.savefig(each_test_result_folder + '/accuracy_weight_diff_combine.jpg', dpi=800)
            plt.close(fig)