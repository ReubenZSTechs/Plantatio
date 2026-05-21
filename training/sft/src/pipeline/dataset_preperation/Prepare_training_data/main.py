from src.pipeline.RAG.retriver import load_vector_db, multi_query_retrieve, get_chunk_map
from src.pipeline.RAG.build_vector_db import Build_vector_DB
from src.pipeline.dataset_preperation.Prepare_training_data.filter_data import filter_good_data
from src.pipeline.dataset_preperation.Prepare_training_data.get_sft_data import build_sft_data
from src.pipeline.dataset_preperation.Prepare_training_data.split_data import split_train_test


from src.utils.CONFIG import CONFIG



def main():
    print("================================================================")

    print("Filetiring Good and bad data")
    filter_good_data(
    csv_filepath=CONFIG["CSV_FILEPATH"],
    eval_k=CONFIG["EVAL_K"],
    good_data_csv_with_dup=CONFIG["GOOD_DATA_CSV_WITH_DUP"],
    good_data_csv_no_dup=CONFIG["GOOD_DATA_CSV_NO_DUP"],
    bad_data_csv=CONFIG["BAD_DATA_CSV"],
    chunk_sep=CONFIG["CHUNK_SEP"],
)
    print("Finnish Filtering")

    print("================================================================")

    print("Split Train and Test Data")
    split_train_test(
        input_csv=CONFIG["GOOD_DATA_CSV_WITH_DUP"],
        train_output=CONFIG["TRAIN_GOOD_DATA_CSV_WITH_DUP"],
        test_output=CONFIG["TEST_GOOD_DATA_CSV_WITH_DUP"],
        test_size=CONFIG["TEST_SIZE"]
    )

    print("Finish Splitting Data")
    print("================================================================")
    
    print("================================================================")

    print("Preparing SFT data")

    build_sft_data(
    input_csv=CONFIG["TRAIN_GOOD_DATA_CSV_WITH_DUP"],
    qr_output=CONFIG["QR_OUTPUT"],
    sel_output=CONFIG["SEL_OUTPUT"],
    gen_output=CONFIG["GEN_OUTPUT"],
    chunk_sep=CONFIG["CHUNK_SEP"],
)
    
    print("Finnish Preparing SFT data")


if __name__ == "__main__":
    main()