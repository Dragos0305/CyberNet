from attackframework import AttackFramework

def main() -> None:
    try:
        attack_framework = AttackFramework()
        attack_framework.start_attack()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()