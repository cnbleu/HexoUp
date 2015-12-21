# View 滑动

常见的滑动方式：

1. 通过 view 本身提供的 scrollTo/scrollBy 方法
2. 通过动画给 View 施加平移效果
3. 通过改变 View 的 LayoutParams 使 View 重新布局

##scrollTo/scrollBy
scrollTo 为绝对滑动，scrollBy 为相对滑动。mScrollX 和 mScrollY 分别等于 View 左边缘与 View 内容左边缘在水平方向的距离，View 上边缘与 View 内容上边缘在竖直方向的距离。scrollTo/scrollBy 只改变 View 内容的位置，不改变 View 在布局中的位置。从左向右以及从上向下滑动时，mScrollX/mScrollY 的值为负值。

##使用动画
动画主要操作 View 的 translationX 和 translationY 属性来实现滑动。View 动画和属性动画都可以实现。View 动画是针对 View 的影像进行操作的，并不能真正改变 View 的位置参数，属性动画不存在这个问题（兼容包实现的属性动画本质仍然是 View 动画）。

##改变布局参数
典型代码如下：

	MarginLayoutParams params = (MarginLayoutParams) button.getLayoutParams();
	params.width += 100;
	params.leftMargin += 100;
	button.requestLayout();
	// 或者 button.setLayoutParams(params);

##弹性滑动
核心思想：将一次大的滑动分成若干次小的滑动，并在一个时间段内完成。

1. invalidate 和 postInvalidate
	invalidate 方法会导致 View 重绘，需要从主线程中调用；
	postInvalidate 会在 view 的 loop 中被调用，也会导致 View 重绘，可以在非主线程中调用。

2. view.computeScroll()
	View 在绘制时，会通过 onDraw 方法调用 View 的 computeScroll 方法。

3. scroller.computeScrollOffset()
	Scroller 的方法，返回 true 表示滑动尚未结束；false 表示已经结束。

4. 通过动画和延时策略。

