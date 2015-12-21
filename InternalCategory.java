/**
 * Copyright © [2013-2015] Magento. All rights reserved.
 * See COPYING.txt for license details.
 */

package com.magentocommerce.mobile.sdk.model.internal.shop;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import org.simpleframework.xml.Element;
import org.simpleframework.xml.ElementList;
import org.simpleframework.xml.Root;

import com.magentocommerce.mobile.sdk.interfaces.ConvertibleModel;
import com.magentocommerce.mobile.sdk.model.shop.Category;
import com.magentocommerce.mobile.sdk.model.shop.CategoryModificators;
import com.magentocommerce.mobile.sdk.model.shop.FilterOption;
import com.magentocommerce.mobile.sdk.model.shop.Image;
import com.magentocommerce.mobile.sdk.model.shop.Product;
import com.magentocommerce.mobile.sdk.model.shop.SimpleCategory;
import com.magentocommerce.mobile.sdk.model.shop.SortOption;
import com.magentocommerce.mobile.sdk.util.Utils;

@Root(name = "category")
public class InternalCategory implements Serializable, ConvertibleModel {//qiangzeng151127

    private static final long serialVersionUID = 1L;

    @Element(name = "category_info", required = false)
    private CategoryInfo categoryInfo;

    @ElementList(name = "items", entry = "item", required = false)
    private List<CategoryItem> categories = new ArrayList<CategoryItem>();

    @ElementList(name = "products", entry = "item", required = false)
    private List<InternalProduct> products = new ArrayList<InternalProduct>();

    @ElementList(name = "filters", entry = "item", required = false)
    private List<Filter> filters = new ArrayList<Filter>();

    @Element(name = "orders", required = false)
    private SortOrdersList sortOrders;

    @SuppressWarnings("unchecked")
    @Override
    public Object convertToPublicModel() {
        Category category = new Category();

        if (categoryInfo != null) {
            category.setParentCategoryId(categoryInfo.getParentCategoryId());
            category.setParentCategoryTitle(categoryInfo.getParentCategoryTitle());
            category.setMoreItemsAvailable(categoryInfo.isMoreItemsAvailable());
            category.setId(categoryInfo.getEntityId());
            category.setTitle(categoryInfo.getLabel());
            List<Image> images = Utils.convertModelsList(categoryInfo.getImages());
            category.setImages(images);
        }

        List<SimpleCategory> subcategories = Utils.convertModelsList(categories);
        category.setSubCategories(subcategories);

        List<Product> productList = Utils.convertModelsList(products);
        category.setProducts(productList);

        CategoryModificators categoryModificators = new CategoryModificators();

        List<FilterOption> filterOptions = Utils.convertModelsList(filters);
        categoryModificators.setFilterOptions(filterOptions);

        if (sortOrders != null) {
            List<SortOption> sortOptions = (List<SortOption>)sortOrders.convertToPublicModel();
            categoryModificators.setSortOptions(sortOptions);
        }

        category.setModificators(categoryModificators);

        return category;
    }

    /**
     * Returns category information.
     *
     * @return category information.
     */
    public CategoryInfo getCategoryInfo() {
        return categoryInfo;
    }

}
