import vk_api


def main():

    login = input("Введите ваш login: ")
    password= input("Введите ваш password: ")
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    vk = vk_session.get_api()

    user_id = input("Введите ID пользователя: ")


    friends = vk.friends.get(user_id=user_id, fields='nickname')
    print("Список друзей:")
    for friend in friends['items']:
        print(f"{friend['first_name']} {friend['last_name']} (id{friend['id']})")


    try:
        albums = vk.photos.getAlbums(owner_id=user_id)
        print("\nНазвания фотоальбомов:")
        for album in albums['items']:
            print(f"{album['title']} (id{album['id']})")
    except vk_api.ApiError as e:
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    main()
