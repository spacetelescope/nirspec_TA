import os
import time
from collections import OrderedDict
from glob import glob

# other code
import testXrandom_stars as tx



"""
DESCRIPTION:
    The script reads the star samples from the text file reference_star_candidate_sets_for_testing.txt provided by
    T. Keyes. The script performs TEST3 and records the following: V2 and V3 offsets, their standard deviation,
    the calculated rotation angle, how many stars get removed in the final fit, which stars where removed,
    and the number of iterations it took to get to the final solution.


NOTES:


    -> Data for testing software with new posatage stamps (as of June 2018) can be located at:
        /grp/jwst/wit4/nirspec/nirspec_TA


     TEST1 - Average positions P1 and P2, transform to V2-V3 space, and compare to average
             reference positions (V2-V3 space)
     TEST2 - Transform individual positions P1 and P2 to V2-V3 space, average V2-V3 space
             positions, and compare to average reference positions.
     TEST3 - Transform P1 and P2 individually to V2-V3 space and compare star by star and
             position by position.
    * Scenes are defined by 100 stars in each detector:
        Scene or scenario 1 = All stars with magnitude 23.0
        Scene or scenario 2 = Magnitude range from 18.0 to 23.0

    * case depends on scene, noise, background value, and shutter velocity; results in 36 files per scene.

    * The tests are performed on ESA data in the following directories on central sotre:
        - /grp/jwst/wit4/nirspec/PFforMaria/Scene_1_AB23
            (which contains 200 closer to "real" stars of magnitude 23: cosmic rays, hot
            pixels, noise, and some shutters closed; and an ideal case)
        - /grp/jwst/wit4/nirspec/PFforMaria/Scene_2_AB1823
            (which contains 200 stars of different magnitudes and also has the "real" data
            as well as the ideal case)
        ** There are 2 sub-folders in each scene: rapid and slow. This is the shutter speed. Both
        sub-cases will be tested.
        ** The simulated data is described in detail in the NIRSpec Technical Note NTN-2015-013, which
        is in /grp/jwst/wit4/nirspec/PFforMaria/Documentation.


"""

#######################################################################################################################


### FUNCTIONS

def get_starsets():
    '''
    This function reads star sets from text file in reference_star_candidate_sets_for_testing.txt

    Returns:
        star_sets = dictionary, contains set number, number of stars in the set, set ID, and the list of star numbers.
    '''
    # read the star sets from the following text file
    star_file = 'OSS_candidate_stars/input_reference_star_sets.txt'
    st = open(star_file, 'r')
    print ('\n Reading star sets from:', star_file)
    # star sets dictionary
    star_sets_dict = OrderedDict()
    for line in st.readlines():
        line.replace("\n", "")
        line_list = line.split()
        star_set = []
        for i, item in enumerate(line_list):
            if i == 0:
                set_number = item
                star_sets_dict[set_number] = {}
            if i == 1:
                star_sets_dict[set_number]["number_of_stars"] = int(item)
            if i == 2:
                star_sets_dict[set_number]["set_ID"] = int(item)
            if i > 2:
                star_set.append(int(item))
            if i == len(line_list)-1:
                star_sets_dict[set_number]["star_set"] = star_set
    st.close()
    return star_sets_dict


#######################################################################################################################



if __name__ == '__main__':


    # SET PARAMETERS
    save_summary_file = True           # Save the text file with main V2 and V3 for all OSS candidate star sets?
    do_plots = False                   # 1. Least squares plot in V2/V3 space showing the true position (0,0)
    #                                       and the mean of the three calculation cases:  Averaging in pixel space,
    #                                       averaging on sky, and no averaging : True or False
    #                                    2. Same plot but instead of the mean show all stars in one 20star calculation
    save_plots = False                 # Save the plots? True or False
    show_plots = True                  # Show the plots? True or False
    output_full_detector = True        # Give resulting coordinates in terms of full detector: True or False
    show_onscreen_results = True       # Want to show on-screen resulting V2s, V3s and statistics? True or False
    show_pixpos_and_v23_plots = False  # Show the plots of x-y and v2-v3 residual positions?
    save_text_file = True              # Want to save the text file of comparison? True or False
    keep_bad_stars = False             # Keep the bad stars in the sample (both positions measured wrong)? True or False
    keep_ugly_stars = True             # Keep the ugly stars (one position measured wrong)? True or False
    perform_abs_threshold = True       # Perform abs_threshold routine (True) or only perform least squares routine (False)
    Nsigma = 2.5                       # N-sigma rejection of bad stars: integer or float
    abs_threshold = 0.32               # threshold to reject points after each iteration of least squares routine, default=0.32
    min_elements = 4                   # minimum number of elements in the absolute threshold least squares routine, default=4
    max_iters_Nsig = 100               # Max number of iterations for N-sigma function: integer

    # set paths
    gen_path = os.path.abspath('OSS_candidate_stars/')
    path4results = '../results_OSScandidatestars/'

    ######################################################


    ### Parameters that will remain unchanged for this script

    # SET PRIMARY PARAMETERS
    detector = 'both'                  # Integer (491 or 492) OR string, 'both' to select stars from both detectors
    save_centroid_disp = False         # Save the display with measured and true positions?
    scene = 1                          # Integer or string, scene=1 is constant Mag 23, scene=2 is stars with Mag 18-23
    background_method = 'frac'         # Select either 'fractional', 'fixed', or None
    background2use = 0.3               # Background to use for analysis: None or float
    shutters = "rapid"                 # Shutter velocity, string: "rapid" or "slow"
    noise = "real"                     # Noise level, string: "nonoise" or "real"
    filter_input = "F140X"             # Filter, string: for now only test case is "F140X"
    test2perform = "T3"                # Test to perform, string: "all", "T1", "T2", "T3" for test 1, 2, and 3, respectively
    show_centroids = False             # Print measured centroid on screen: True or False
    show_disp = False                  # Show display of resulting positions? (will show 2 figs, same but different contrast)
    Pier_corr = True                   # Include Pier's corrections to measured positions
    tilt = False                       # Tilt angle: True or False
    backgnd_subtraction_method = 1     # 1    = Do background subtraction on final image (after subtracting 3-2 and 2-1),
    #                                           before converting negative values into zeros
    #                                    2    = Do background subtraction on 3-2 and 2-1 individually
    #                                    None = Do not subtract background
    # SET SECONDARY PARAMETERS THAT CAN BE ADJUSTED
    checkbox_size = 3                  # Real checkbox size
    xwidth_list = [3, 5, 7]            # Number of rows of the centroid region
    ywidth_list = [3, 5, 7]            # Number of columns of the centroid region
    vlim = (1, 100)                    # Sensitivity limits of image, i.e. (0.001, 0.1)
    threshold = 0.01                   # Convergence threshold of accepted difference between checkbox centroid and coarse location
    max_iter = 10                      # Maximum number of iterations for finding coarse location
    verbose = False                    # Show some debug messages (i.e. resulting calculations)
    debug = False                      # See all debug messages (i.e. values of variables and calculations)
    arcsecs = True                     # Final units in arcsecs? True or False (=degrees)
    determine_moments = False          # Want to determine 2nd and 3rd moments?
    display_master_img = False         # Want to see the combined ramped images for every star?
    random_sample = False              # choose a random sample of stars from either detector: True or False


    ### CODE

    # start the timer to compute the whole running time
    start_time = time.time()

    # make sure that bad stars are gone if ugly stars are to be gone as well
    if not keep_ugly_stars:
        keep_bad_stars = False

    # Set variable as it appears defined in function
    if perform_abs_threshold:
        just_least_sqares = False  # Only perform least squares routine = True, perform abs_threshold routine = False
    else:
        just_least_sqares = True

    # Prepare the text files with final results for all star sets analyzed
    col_hdr = '{:<12} {:>18} {:>18} {:>20} {:>20} {:>20} {:>10} {:>10} {:>20}'.format('# Star_Set', 'mean_V2',
                                                                                    'mean_V3', 'sigma_V2',
                                                                                    'sigma_V3', 'theta',
                                                                                    'Iter', 'Removed_stars',
                                                                                    'Removed_stars_numbers')
    if save_summary_file:
        print("Creating summary files... ")
        star_sets_textfile_Cwin3 = os.path.join(path4results, 'OSScandidates_results_Cwin3.txt')
        star_sets_textfile_Cwin5 = os.path.join(path4results, 'OSScandidates_results_Cwin5.txt')
        star_sets_textfile_Cwin7 = os.path.join(path4results, 'OSScandidates_results_Cwin7.txt')
        print(star_sets_textfile_Cwin3)
        with open(star_sets_textfile_Cwin3, 'w') as sstf3:
            sstf3.write(col_hdr+"\n")
        with open(star_sets_textfile_Cwin5, 'w') as sstf5:
            sstf5.write(col_hdr+"\n")
        with open(star_sets_textfile_Cwin7, 'w') as sstf7:
            sstf7.write(col_hdr+"\n")
        print("   Done.")

    # get the star sets from the text file
    star_sets_dict = get_starsets()

    for star_set_number, set_dict in star_sets_dict.items():
        # order the star list from lowest to highest number
        stars_sample = set_dict["star_set"]
        stars_sample.sort(key=lambda xx: xx)

        # Determine number of stars in sample
        stars_in_sample = len(stars_sample)                # Number of stars in sample

        # Compact variables
        primary_params1 = [do_plots, save_plots, show_plots, detector, output_full_detector, show_onscreen_results,
                           show_pixpos_and_v23_plots, save_text_file]
        primary_params2 = [save_centroid_disp, keep_bad_stars, keep_ugly_stars, just_least_sqares, stars_in_sample,
                           scene, background_method, background2use]
        primary_params3 = [shutters, noise, filter_input, test2perform, Nsigma, abs_threshold, abs_threshold, min_elements,
                           max_iters_Nsig]
        primary_params = [primary_params1, primary_params2, primary_params3]
        secondary_params1 = [checkbox_size, xwidth_list, ywidth_list, vlim, threshold, max_iter, verbose]
        secondary_params2 = [debug, arcsecs, determine_moments, display_master_img, show_centroids, show_disp]
        secondary_params3 = [Pier_corr, tilt, backgnd_subtraction_method, random_sample]
        secondary_params = [secondary_params1, secondary_params2, secondary_params3]

        # run the test and get resutls
        set_ID = set_dict["set_ID"]
        extra_string = '_starset'+repr(set_ID)
        print ("Running test for star set number: ", star_set_number, ", which is set ID : ", extra_string)
        results_all_tests = tx.run_testXrandom_stars(stars_sample, primary_params, secondary_params,
                                                     path4results, gen_path, extra_string)
        if save_text_file:
            # Rename the output test files according to the set ID so that files do not get overwritten in the
            # directory resultsXrandomstars.
            txtfiles_in_resultsXrandomstars = glob("../resultsXrandomstars/*.txt")
            for txtXran in txtfiles_in_resultsXrandomstars:
                if "starster" not in txtXran:
                    txtXran.replace(".txt", extra_string+".txt")


        for resTest in results_all_tests:
            # unfold variables per centroid window results_all_tests[0][5][s][width]
            case, new_stars_sample, Tbench_Vs, T_Vs, T_diffVs, LS_res, LS_info = resTest
            nw_stars_sample3, nw_stars_sample5, nw_stars_sample7 = new_stars_sample
            Tbench_V2_3, Tbench_V3_3, Tbench_V2_5, Tbench_V3_5, Tbench_V2_7, Tbench_V3_7 = Tbench_Vs
            TV2_3, TV3_3, TV2_5, TV3_5, TV2_7, TV3_7 = T_Vs
            TdiffV2_3, TdiffV3_3, TdiffV2_5, TdiffV3_5, TdiffV2_7, TdiffV3_7 = T_diffVs
            TLSsigmas_3, TLSsigmas_5, TLSsigmas_7, TLSdeltas_3, TLSdeltas_5, TLSdeltas_7 = LS_res
            iterations, rejected_elementsLS = LS_info

            milliarcsec = True
            if milliarcsec:
                TdiffV2_3 = tx.convert2milliarcsec(TdiffV2_3)
                TdiffV3_3 = tx.convert2milliarcsec(TdiffV3_3)
                TdiffV2_5 = tx.convert2milliarcsec(TdiffV2_5)
                TdiffV3_5 = tx.convert2milliarcsec(TdiffV3_5)
                TdiffV2_7 = tx.convert2milliarcsec(TdiffV2_7)
                TdiffV3_7 = tx.convert2milliarcsec(TdiffV3_7)
                TLSsigmas_3 = tx.convert2milliarcsec(TLSsigmas_3)
                TLSsigmas_5 = tx.convert2milliarcsec(TLSsigmas_5)
                TLSsigmas_7 = tx.convert2milliarcsec(TLSsigmas_7)
                TLSdeltas_3 = tx.convert2milliarcsec(TLSdeltas_3)
                TLSdeltas_5 = tx.convert2milliarcsec(TLSdeltas_5)
                TLSdeltas_7 = tx.convert2milliarcsec(TLSdeltas_7)

        # Record results per centroid window
        for cwin in xwidth_list:
            cwincase = case+'_CentroidWindow'+repr(cwin)

            # Output per centroid window size
            if cwin == 3:
                s, d, v = 0, 3, 0
            if cwin == 5:
                s, d, v = 1, 4, 2
            if cwin == 7:
                s, d, v = 2, 5, 4
            if test2perform != "all":
                T1sigmaV2 = results_all_tests[0][5][s][0]   # Test ran sigma V2 value
                T1sigmaV3 = results_all_tests[0][5][s][1]   # Test ran sigma V3 value
                T1sigma_theta = results_all_tests[0][5][s][2]   # Test ran sigma theta value
                T1meanV3 = results_all_tests[0][5][d][1]    # Test ran mean V3 value
                T1meanV2 = results_all_tests[0][5][d][0]    # Test ran mean V2 value
                T1mean_theta = results_all_tests[0][5][d][2]   # Test ran sigma theta value
                if test2perform == "T1":
                    labels_list = ['Avg in Pixel Space']
                if test2perform == "T2":
                    labels_list = ['Avg in Sky']
                if test2perform == "T3":
                    labels_list = ['No Avg']
                arrx = [T1meanV2]
                arry = [T1meanV3]
                print_side_values = [T1sigmaV2, T1meanV2, T1sigmaV3, T1meanV3]
            if test2perform == "all":
                T2sigmaV2 = results_all_tests[1][5][s][0]   # Test 2
                T2sigmaV3 = results_all_tests[1][5][s][1]   # Test 2
                T2meanV2 = results_all_tests[1][5][d][0]    # Test 2
                T2meanV3 = results_all_tests[1][5][d][1]    # Test 2
                T3sigmaV2 = results_all_tests[2][5][s][0]   # Test 3
                T3sigmaV3 = results_all_tests[2][5][s][1]   # Test 3
                T3meanV2 = results_all_tests[2][5][d][0]    # Test 3
                T3meanV3 = results_all_tests[2][5][d][1]    # Test 3
                labels_list = ['Avg in Pixel Space', 'Avg in Sky', 'No Avg']
                arrx = [T1meanV2, T2meanV2, T3meanV2]
                arry = [T1meanV3, T2meanV3, T3meanV3]
                print_side_values = [T1sigmaV2, T1meanV2, T2sigmaV2, T2meanV2, T3sigmaV2, T3meanV2,
                                     T1sigmaV3, T1meanV3, T2sigmaV3, T2meanV3, T3sigmaV3, T3meanV3]

            # use the index to collect the star numbers of the rejected stars
            to_stars_removed = len(rejected_elementsLS[s])
            rejected_stars = []
            stars_in_set = []
            for st_s in stars_sample:
               stars_in_set.append(st_s)
            if test2perform == 'T3':
                for st_s in stars_sample:
                   stars_in_set.append(st_s)
            if to_stars_removed > 0:
                for idx_re in rejected_elementsLS[s]:
                    rejected_stars.append(stars_in_set[idx_re])
            # print final results for each centroid window of each test
            line2print = '{:<12} {:>20} {:>20} {:>20} {:>20} {:>20} {:>6} {:>10} {:>20}'.format(star_set_number, T1meanV2, T1meanV3,
                                                                                        print_side_values[0],
                                                                                        print_side_values[2],
                                                                                        T1mean_theta,
                                                                                        iterations[s], to_stars_removed,
                                                                                        repr(rejected_stars))
            print('Centroid Window of '+repr(cwin)+'x'+repr(cwin)+' pixels: ')
            print (col_hdr)
            print (line2print)
            if save_summary_file:
                with open(star_sets_textfile_Cwin3, 'a') as tf:
                    if cwin == 5:
                        tf = open(star_sets_textfile_Cwin5, 'a')
                    if cwin == 7:
                        tf = open(star_sets_textfile_Cwin7, 'a')
                    tf.write(line2print+"\n")
        print("Lines added to text files.")


    print ("\n Script 'OSScandidatestars.py' finished! Took  %s  seconds to finish. \n" % (time.time() - start_time))
