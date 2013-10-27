from pmg_backend import app as app_backend


if __name__ == "__main__":
    # run Flask dev-server
    app_backend.run(port=5001)