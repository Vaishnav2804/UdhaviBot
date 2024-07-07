from llm_setup.llm_setup import LLMService
import config as config

if __name__ == '__main__':
    config.set_envs()
    llm_svc = LLMService()

    llm, err = llm_svc.get_llm()
    if err is not None:
        print(f"Error in getting llm: {err}")

    print(str(llm.invoke("What can you do?")))
