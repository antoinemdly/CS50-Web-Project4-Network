function display_profile(user,page){
    display_post(user,page)
}

// function that display all the post in the #posts div
function display_post(category,page){
    block = document.querySelector('#posts')
        block.innerHTML = ""
        let url;
        // if page is given, query a specific page
        if (page){
            url = `/posts/${category}?page=${page}`
        }
        // if not all the posts in this category are returned
        else {
            url = `/posts/${category}`
        }
        // fetch the posts
        fetch(url, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            // followers is a field in the response if a valid user is submited as the category
            // if there is, a user info div is added at the top with all the info and a button is added to follow a user (if you are on your own profile no button is displayed)
            if ('followers' in data) {
                const user = document.createElement('h2')
                const followers = document.createElement('p')
                const followed = document.createElement('p')

                user.innerHTML = category
                followers.innerHTML = `followers : ${data['followers']}`
                followed.innerHTML = `followed users : ${data['following']}`

                // check if the user is already on the user profile
                // otherwise when adding the divs are added without removing the current one
                const user_info = document.querySelector('#user_info')
                if (user_info){
                    user_info.children[0].replaceWith(user)
                    user_info.children[1].replaceWith(followers)
                    user_info.children[2].replaceWith(followed)
                }
                else{
                    const div = document.createElement('div')
                    div.id = 'user_info'

                    div.innerHTML = ''
                    div.appendChild(user)
                    div.appendChild(followers)
                    div.appendChild(followed)

                    const body = document.querySelector('.body')
                    body.insertBefore(div, body.firstChild)

                    authenticated()
                    .then(response => {
                        if (response) {
                            if (!data['IsSelf']){
                                const follow_button = document.createElement('button')
                                follow_button.id = 'follow_button'
            
                                updateFollowButton(category)
            
                                document.querySelector('#user_info').appendChild(follow_button);
                            }
                        }
                    })
                }
            }
          
            // handle the active state or not of the numbered page in the nav bar at the bottom
            
            document.querySelectorAll('.page_li').forEach(element => {
                // remove active class on all the paginator elements
                element.classList.remove('active');

                // if the page is not available, the button is disabled (not enough posts)
                const button = element.firstChild
                element.classList.toggle('disabled', button.dataset.page > data['num_pages'])
            });

            // highlight the current page the user is on
            const page_button = document.querySelector(`#page${data['current_page']}`);
            if (page_button){
                page_button.parentElement.classList.add('active')
            }

            // handles previous and next button and disabled them if the previous or next page doesnt exist
            document.querySelector('#previous').classList.toggle('disabled', !data['has_previous']);
            document.querySelector('#next').classList.toggle('disabled', !data['has_next']);

            // create for each post a div
            data['posts'].forEach((post, index) => {
                const user = document.createElement('a')
                const content = document.createElement('p')
                const date = document.createElement('p')
                const like_div = document.createElement('div')
                like_div.className = 'like_div'
                const image_container = document.createElement('div')
                const like_logo = document.createElement('img')
                like_logo.src = 'https://media.licdn.com/dms/image/v2/C5612AQEDZFEAMuBvhQ/article-inline_image-shrink_1000_1488/article-inline_image-shrink_1000_1488/0/1574268202725?e=1730937600&v=beta&t=sBRdjCPEiFUx6TVAhX0WWIb-OKHfknSgiDcCiAi3GPY'
                const likes = document.createElement('p')
                image_container.appendChild(like_logo)
                like_div.appendChild(likes)
                like_div.appendChild(image_container)

                const div = document.createElement('div')
                div.className = 'post_div'
                user.innerHTML = post['user']
                user.dataset.username = post['user']
                user.href = '#'
                user.className = 'user_profile'
                content.innerHTML = post['content']
                date.innerHTML = post['date']
                likes.innerHTML = post['likes']

                setTimeout(() => {
                    div.classList.add("show");
                }, index * 200);

                // if user is logged in add a like button
                authenticated()
                .then(response => {
                    if (response){
                        const like_button = document.createElement('button')
                        like_button.innerHTML = 'like'
                        const unlike_button = document.createElement('button')
                        unlike_button.innerHTML = 'unlike'
                        like_button.addEventListener('click', function(){
                            like_button.replaceWith(unlike_button)
                            fetch('api', {
                                method: 'PUT',
                                body: JSON.stringify({
                                    like: post['id'],
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log(data)
                                likes.innerHTML++;
                            })
                        })
                        unlike_button.addEventListener('click', function(){
                            unlike_button.replaceWith(like_button)
                            fetch('api', {
                                method: 'PUT',
                                body: JSON.stringify({
                                    unlike: post['id'],
                                    
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log(data)
                                likes.innerHTML--
                            })
                        })
    
                        fetch('api', {
                            method: 'POST',
                            body: JSON.stringify({
                                isLiked: post['user'],
                                post_id: post['id'],
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data){
                                div.appendChild(unlike_button)    
                            }
                            else{
                                div.appendChild(like_button)
                            }
                        })
                    }
                })
                
                // if the user is the owner of the post add a edit button
                fetch('api', {
                    method: 'POST',
                    body: JSON.stringify({
                        isMyPost: post['user'],
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data){
                        const edit_button = document.createElement('button')
                        edit_button.innerHTML = 'edit'
                        edit_button.className = 'edit_button'
                        div.appendChild(edit_button)

                        edit_button.addEventListener('click', function() {
                            const content_div = document.createElement('div')
                            const new_content = document.createElement('textarea')
                            const save_button = document.createElement('button')

                            content_div.appendChild(new_content)

                            new_content.value = content.innerHTML
                            save_button.innerHTML = 'Save'

                            content.replaceWith(content_div)
                            edit_button.replaceWith(save_button)

                            save_button.addEventListener('click', function() {

                                fetch('api', {
                                    method: 'PUT',
                                    body: JSON.stringify({
                                        edit_post: new_content.value,
                                        post_id: post['id'],
                                    })
                                })
                                .then(response => response.json())
                                .then(data => {
                                    console.log(data)

                                    content.innerHTML = new_content.value
                                    content_div.replaceWith(content)

                                    save_button.replaceWith(edit_button)
                                })
                            })
                        })
                    }
                })

                div.appendChild(user)
                div.appendChild(content)
                div.appendChild(date)
                div.appendChild(like_div)

                block.appendChild(div)
            });
        })

        block.style.display = 'block'
}

function resetAnimation(element) {
    element.style.animation = 'none';
    element.offsetHeight;
    element.style.animation = '';
}

function authenticated() {
    return fetch('api', {
        method: 'POST',
        body: JSON.stringify({
            authenticated: '?',
        })
    })
    .then(response => response.json())
    .then(data => {
        return data ? true : false;
    })
}

// return true if the logged in user if following 'user'
function isFollowed(user) {
    return fetch('api', {
        method: 'POST',
        body: JSON.stringify({
            followed: user,
        })
    })
    .then(response => response.json())
    .then(data => {
        return data ? true : false;
    })
}

function updateFollowButton(category) {
    isFollowed(category)
    .then(response => {
        if (response){
            follow_button.innerHTML = `Unfollow ${category}`
            follow_button.addEventListener('click', function() {
                fetch('api', {
                    method: 'PUT',
                    body: JSON.stringify({
                        unfollow: category,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    updateFollowButton(category)
                })
            })
        }
        else {
            follow_button.innerHTML = `Follow ${category}`
            follow_button.addEventListener('click', function() {
                fetch('api', {
                    method: 'PUT',
                    body: JSON.stringify({
                        follow: category,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    updateFollowButton(category)
                })
            })
        }
    })
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}