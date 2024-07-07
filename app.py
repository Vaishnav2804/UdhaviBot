import logging

from llm_setup.llm_setup import LLMService
import config as config

if __name__ == '__main__':
    # logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # set environment variables
    config.set_envs()

    # get llm service
    llm_svc = LLMService(logger)
    if llm_svc.error is not None:
        print(f"Error in initializing llm service: {llm_svc.error}")
        exit(0)

    # get llm instance to make llm calls
    llm, err = llm_svc.get_llm()
    if err is not None:
        print(f"Error in getting llm: {err}")
        exit(0)

    print(str(llm.invoke("What can you do?")))
